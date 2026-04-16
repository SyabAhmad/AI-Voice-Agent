from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import health, webhook
from app.core.logger import logger

app = FastAPI(
    title="Voice AI Appointment Booking Agent",
    description="AI-powered voice agent for appointment booking",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["Health"])
app.include_router(webhook.router, tags=["Webhook"])


@app.on_event("startup")
async def startup_event():
    logger.info("Starting Voice AI Agent...")
    try:
        from app.services import crm_service

        crm_service.get_google_sheet()
        logger.info("Google Sheets CRM connected")
    except Exception as e:
        logger.warning(f"Google Sheets not connected at startup: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Voice AI Agent...")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
