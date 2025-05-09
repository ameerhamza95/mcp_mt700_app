import requests
import json
from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
from pydantic import BaseModel
import uvicorn
import nest_asyncio
from fastapi.responses import HTMLResponse
import logging
from mcpServer import generate_mt700_response

# Configure logging
logging.basicConfig(level=logging.INFO, force=True)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
api_app = FastAPI()

# Initialize MCP server
mcp = FastApiMCP(
    api_app,
    name="PO_INV_MT700_MCP",
    description="MCP server for generating MT700 from PO and INV via hive.t",
)

# Pydantic model for input validation (optional)
class POINVRequest(BaseModel):
    po_number: str
    inv_number: str

# Root endpoint for testing
@api_app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <h1>PO_INV MT700 MCP Server</h1>
    <p>Server is running. Access MCP tools at /mcp or try /generate_mt700?po_number=PO-0001&inv_number=INV-0006</p>
    """

# Endpoint to generate MT700
@api_app.get("/generate_mt700", operation_id="generate_mt700")
async def generate_mt700(po_number: str, inv_number: str):
    try:
        logger.info("Received request for po_number: %s, inv_number: %s", po_number, inv_number)
        mt700_response = generate_mt700_response(po_number, inv_number)
        return mt700_response
    except Exception as e:
        logger.error("Error processing request for po_number %s and inv_number %s: %s", po_number, inv_number, str(e))
        raise

# Mount the MCP server
mcp.mount()

if __name__ == "__main__":
    nest_asyncio.apply()
    uvicorn.run(api_app, host="localhost", port=8000)