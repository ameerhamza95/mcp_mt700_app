import requests
import json
from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
from pydantic import BaseModel
import uvicorn
import nest_asyncio
from fastapi.responses import HTMLResponse
import logging

# Configure logging with forced output to console
logging.basicConfig(level=logging.INFO, force=True)
logger = logging.getLogger(__name__)

# Function to call API and extract data
def fetch_data(endpoint: str, document_id: str, document_type: str) -> dict:
    try:
        url = f"http://20.8.88.74:7081{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        params = {"documentId": document_id, "type": document_type}
        response = requests.post(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        logger.info("Fetched data for %s (%s): %s", document_id, document_type, data)
        return data
    except Exception as e:
        logger.error("Failed to fetch data for %s (%s): %s", document_id, document_type, str(e))
        raise

# Function to extract SalesAgreement from PO response
def extract_sales_agreement(po_response: dict) -> str:
    try:
        message = json.loads(po_response["message"])
        data = json.loads(message["data"])
        sales_agreement = data["note"]
        logger.info("Extracted SalesAgreement: %s", sales_agreement)
        return sales_agreement
    except Exception as e:
        logger.error("Failed to extract SalesAgreement: %s", str(e))
        raise

# Function to generate MT700-like response
def generate_mt700_response(po_number: str, inv_number: str) -> dict:
    try:
        # Fetch PO data
        po_response = fetch_data("/api/mywave/trade/document/load", po_number, "purchaseorder")
        sales_agreement = extract_sales_agreement(po_response)

        # Fetch INV data
        inv_response = fetch_data("/api/mywave/trade/document/load", inv_number, "invoice")

        # Prepare final API call with SalesAgreement
        final_url = "http://20.8.88.74:7081/api/mywave/chatgpt/mt700withreference"
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        payload = {
            "PURCHASEORDER": po_number,
            "PROFORMAINVOICE": inv_number,
            "SalesAgreement": sales_agreement
        }
        final_response = requests.post(final_url, json=payload, headers=headers)
        final_response.raise_for_status()
        result = final_response.json()

        logger.info("Generated MT700 response for PO %s and INV %s: %s", po_number, inv_number, result)
        return result
    except Exception as e:
        logger.error("Failed to generate MT700 response for PO %s and INV %s: %s", po_number, inv_number, str(e))
        raise



