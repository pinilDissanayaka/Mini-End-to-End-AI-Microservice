from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv, find_dotenv
from database import Base, engine
from routes.routes import router
from fastapi.exception_handlers import RequestValidationError
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from fastapi import Request
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from utils import logger, config


app = FastAPI(
    title=config.APP_NAME,
    description=config.APP_DESCRIPTION,
    version=config.APP_VERSION,
)


app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=config.CORS_ALLOW_CREDENTIALS,
    allow_methods=config.CORS_ALLOW_METHODS,
    allow_headers=config.CORS_ALLOW_HEADERS,
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
