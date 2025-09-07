"""
FastAPI Backend for Document Processing
Deployed on Google Cloud Run
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks, status, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import uuid
import asyncio
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import io
import fitz
from docx import Document
from collections import defaultdict

# Import our professional DocParse module
from docparse import DocParseEngine, ProcessingOptions, extract_document

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app for API only
# Security: Disable docs in production
import os
PRODUCTION = os.getenv("ENVIRONMENT", "development") == "production"

app = FastAPI(
    title="DocParse API - Document Processing Service",
    description="Backend API for converting PDF, TXT, and DOCX files to structured JSON format",
    version="1.0.0",
    docs_url=None if PRODUCTION else "/docs",
    redoc_url=None if PRODUCTION else "/redoc",
    openapi_url=None if PRODUCTION else "/openapi.json"
)

# CORS configuration - Allow your Vercel frontend
# Prefer explicit domains via FRONTEND_ORIGINS env (comma-separated).
# Additionally, allow any Vercel subdomain via regex.
frontend_origins_env = os.getenv("FRONTEND_ORIGINS", "").strip()
explicit_origins = [o.strip() for o in frontend_origins_env.split(",") if o.strip()]

default_local_origins = [
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=default_local_origins + explicit_origins,
    allow_origin_regex=r"https://.*\\.vercel\\.app",
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

# Configuration for Cloud Run - Handle large files efficiently
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB - Optimal balance
SUPPORTED_EXTENSIONS = {"pdf", "txt", "docx"}

# Simple rate limiting (in production, use Redis or proper middleware)
request_counts = defaultdict(list)
RATE_LIMIT = 10  # requests per minute per IP

# Initialize DocParse engine
doc_engine = DocParseEngine()

# Pydantic models
class ConversionResponse(BaseModel):
    """Response model for successful conversion"""
    success: bool = Field(True)
    message: str = Field(description="Status message")
    metadata: Dict[str, Any] = Field(description="Document metadata")
    processing_time: float = Field(description="Processing time in seconds")

class ErrorResponse(BaseModel):
    """Response model for errors"""
    success: bool = Field(False)
    error: str = Field(description="Error message")
    error_code: str = Field(description="Error code")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field("healthy")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    version: str = Field("1.0.0")
    max_file_size_mb: int = Field(default_factory=lambda: MAX_FILE_SIZE // (1024*1024))

# Utility functions
def check_rate_limit(client_ip: str) -> bool:
    """Simple rate limiting check"""
    now = datetime.now()
    minute_ago = now - timedelta(minutes=1)
    
    # Clean old requests
    request_counts[client_ip] = [
        req_time for req_time in request_counts[client_ip] 
        if req_time > minute_ago
    ]
    
    # Check if under limit
    if len(request_counts[client_ip]) >= RATE_LIMIT:
        return False
    
    # Add current request
    request_counts[client_ip].append(now)
    return True

async def validate_file(file: UploadFile) -> tuple[bool, Optional[str]]:
    """Comprehensive file validation"""
    try:
        if not file.filename:
            return False, "No filename provided"
        
        if not doc_engine.is_supported_file(file.filename):
            supported = ", ".join(SUPPORTED_EXTENSIONS)
            return False, f"Unsupported file type. Supported formats: {supported}"
        
        await file.seek(0)
        
        # Check file size
        size = 0
        chunk_size = 8192
        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            size += len(chunk)
            if size > MAX_FILE_SIZE:
                await file.seek(0)
                return False, f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
        
        await file.seek(0)
        return True, None
        
    except Exception as e:
        logger.error(f"File validation error: {e}")
        return False, f"File validation failed: {str(e)}"

async def save_uploaded_file(file: UploadFile) -> Path:
    """Save uploaded file securely"""
    unique_id = str(uuid.uuid4())
    filename = file.filename
    name, ext = os.path.splitext(filename)
    safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    unique_filename = f"{safe_name}_{unique_id}{ext}"
    
    import tempfile
    temp_dir = Path(tempfile.gettempdir())
    file_path = temp_dir / unique_filename
    
    content = await file.read()
    with open(file_path, 'wb') as f:
        f.write(content)
    
    logger.info(f"Saved uploaded file: {unique_filename}")
    return file_path

async def process_document_async(file_path: Path, options: ProcessingOptions) -> Dict[str, Any]:
    """Async wrapper for document processing"""
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, doc_engine.extract_text, file_path, options)
        
        if result.success:
            logger.info(f"Successfully processed {file_path.name}")
            return result.to_dict()
        else:
            logger.error(f"Processing failed for {file_path.name}: {result.error_message}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=result.error_message
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing {file_path.name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document processing failed: {str(e)}"
        )

async def cleanup_old_files():
    """Background cleanup task"""
    try:
        logger.info("Background cleanup completed")
        return 0
    except Exception as e:
        logger.error(f"Cleanup error: {e}")
        return 0

# API Routes
@app.get("/", response_model=HealthResponse)
async def root():
    """API root endpoint"""
    return HealthResponse()

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse()

@app.post("/api/upload")
async def upload_file(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Document file to convert (PDF, TXT, DOCX)"),
    max_pages: Optional[int] = Form(None, description="Maximum number of pages to process")
):
    """Upload and convert document file to JSON"""
    file_path = None
    try:
        # Rate limiting check
        client_ip = request.client.host
        if not check_rate_limit(client_ip):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=429, 
                detail="Rate limit exceeded. Please try again later."
            )
        
        if not file.filename:
            logger.error("No file selected in upload request")
            raise HTTPException(status_code=400, detail="No file selected")
        
        logger.info(f"Processing upload request for file: {file.filename}")
        
        # Validate file
        is_valid, error_msg = await validate_file(file)
        if not is_valid:
            logger.error(f"File validation failed: {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Save uploaded file temporarily
        file_path = await save_uploaded_file(file)
        logger.info(f"File saved temporarily: {file_path.name}")
        
        # Extract text and convert to JSON using DocParse
        options = ProcessingOptions(max_pages=max_pages)
        extracted_data = await process_document_async(file_path, options)
        
        # Create JSON string for download
        json_string = json.dumps(extracted_data, indent=2, ensure_ascii=False)
        json_filename = f"{file.filename.rsplit('.', 1)[0]}_converted.json"
        
        logger.info(f"Successfully processed {file.filename}, returning JSON file")
        
        # Schedule background cleanup
        background_tasks.add_task(cleanup_old_files)
        
        # Return JSON as downloadable file
        return StreamingResponse(
            io.BytesIO(json_string.encode('utf-8')),
            media_type='application/json',
            headers={
                "Content-Disposition": f"attachment; filename={json_filename}",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
        
    except HTTPException as he:
        logger.error(f"HTTP Exception in upload: {str(he)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in upload: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Internal server error occurred during processing",
                "error_code": "INTERNAL_SERVER_ERROR"
            }
        )
    finally:
        # Clean up uploaded file
        if file_path and file_path.exists():
            try:
                file_path.unlink()
                logger.info(f"Cleaned up temporary file: {file_path}")
            except Exception as cleanup_error:
                logger.warning(f"Failed to cleanup file {file_path}: {cleanup_error}")

@app.post("/api/process-url")
async def process_from_url(
    background_tasks: BackgroundTasks,
    file_url: str = Form(..., description="URL to document file"),
    max_pages: Optional[int] = Form(None, description="Maximum number of pages to process")
):
    """Process document from URL (for very large files)"""
    import requests
    from urllib.parse import urlparse
    
    file_path = None
    try:
        logger.info(f"Processing document from URL: {file_url}")
        
        # Download file from URL
        response = requests.get(file_url, timeout=60)
        response.raise_for_status()
        
        # Get filename from URL or Content-Disposition header
        filename = urlparse(file_url).path.split('/')[-1]
        if not filename or '.' not in filename:
            content_disposition = response.headers.get('Content-Disposition', '')
            if 'filename=' in content_disposition:
                filename = content_disposition.split('filename=')[1].strip('"')
            else:
                filename = "document.pdf"  # default
        
        # Save to temp file
        unique_id = str(uuid.uuid4())
        name, ext = os.path.splitext(filename)
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        unique_filename = f"{safe_name}_{unique_id}{ext}"
        
        import tempfile
        temp_dir = Path(tempfile.gettempdir())
        file_path = temp_dir / unique_filename
        
        with open(file_path, 'wb') as f:
            f.write(response.content)
        
        logger.info(f"Downloaded file from URL: {file_path.name}")
        
        # Process the file
        options = ProcessingOptions(max_pages=max_pages)
        extracted_data = await process_document_async(file_path, options)
        
        # Create JSON response
        json_string = json.dumps(extracted_data, indent=2, ensure_ascii=False)
        json_filename = f"{filename.rsplit('.', 1)[0]}_converted.json"
        
        logger.info(f"Successfully processed file from URL, returning JSON")
        
        # Schedule background cleanup
        background_tasks.add_task(cleanup_old_files)
        
        return StreamingResponse(
            io.BytesIO(json_string.encode('utf-8')),
            media_type='application/json',
            headers={
                "Content-Disposition": f"attachment; filename={json_filename}",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
        
    except Exception as e:
        logger.error(f"Error processing URL: {str(e)}", exc_info=True)
        return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": "Failed to process document from URL",
                    "error_code": "URL_PROCESSING_ERROR"
                }
            )
    finally:
        # Clean up downloaded file
        if file_path and file_path.exists():
            try:
                file_path.unlink()
                logger.info(f"Cleaned up downloaded file: {file_path}")
            except Exception as cleanup_error:
                logger.warning(f"Failed to cleanup file {file_path}: {cleanup_error}")

# Export for Cloud Run
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
