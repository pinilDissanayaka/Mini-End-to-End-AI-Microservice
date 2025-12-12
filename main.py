from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv, find_dotenv
from database import Base, engine
from routes.vector_store import vector_store_router
from routes.chat import chat_router
from routes.lead import lead_generator_router
from routes.support_ticket import support_ticket_router
from routes.settings import settings_router
from routes.ws import ws_router
from routes.dashboard import dashboard_router
from routes.onboarding import onboarding_router
from routes.routes import router as document_qa_router
from fastapi.exception_handlers import RequestValidationError
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from fastapi import Request
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from utils import logger


app = FastAPI(
    title="Mini End-to-End AI Microservice",
    description="AI-powered document QA service with RAG capabilities. Upload documents, extract embeddings, and query using LLMs.",
    version="1.0.0",
)


# Include document QA routes (assignment requirement)
app.include_router(document_qa_router)

# Include existing routes
app.include_router(vector_store_router)
app.include_router(chat_router)
app.include_router(lead_generator_router)
app.include_router(support_ticket_router)
app.include_router(settings_router)
app.include_router(ws_router)
app.include_router(dashboard_router)
app.include_router(onboarding_router, prefix="/v1")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup():
    """
    The event handler that is called when the application is starting up.

    Initializes the database by creating the tables in the database.

    This function is called by FastAPI when the application is starting up.
    """

    load_dotenv(find_dotenv())
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
@app.get("/")
async def health_check():
    """
    Check if the API is running.

    Returns a JSON response with a message and a 200 status code.
    """
    return JSONResponse(content={"message": "API is running."}, status_code=200)
    
    
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Handle any unhandled exception raised during the request.

    The handler logs the exception using the error level, and returns a JSON response
    with a 500 status code and a generic error message.

    :param request: The request that caused the exception.
    :param exc: The exception that was raised.
    :return: A JSON response with a 500 status code and a generic error message.
    """
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handle any HTTPException raised during the request.

    The handler logs the exception using the warning level, and returns a JSON response
    with the same status code and a generic error message.

    :param request: The request that caused the exception.
    :param exc: The exception that was raised.
    :return: A JSON response with the same status code and a generic error message.
    """
    logger.warning(f"HTTPException: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle any RequestValidationError raised during the request.

    The handler logs the exception using the warning level, and returns a JSON response
    with a 422 status code and a dictionary containing the validation errors.

    :param request: The request that caused the exception.
    :param exc: The exception that was raised.
    :return: A JSON response with a 422 status code and a dictionary containing the validation errors.
    """
    
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )


if __name__ == "__main__":
    load_dotenv(find_dotenv())
    uvicorn.run("main:app", host="0.0.0.0", port=8070)
