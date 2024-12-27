import uvicorn
from fastapi import FastAPI
from api.v1.data_router import router as data_router
from api.v1.model_router import router as model_router
from services.logging_config import setup_logging


logger = setup_logging()

app = FastAPI(
    title="Financial Instrument Prediction API",
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
)


# Include routers
app.include_router(data_router, prefix="/api/v1/data", tags=["Data"])
app.include_router(model_router, prefix="/api/v1/model", tags=["Model"])

@app.get("/")
async def root():
    logger.info("Root endpoint")
    return {"message": "Welcome to Financial Instrument Prediction API"}


if __name__ == "__main__":
    logger.info("Starting the application")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
