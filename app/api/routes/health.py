from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "voice-ai-agent", "version": "1.0.0"}


@router.get("/")
async def root():
    return {
        "message": "Voice AI Appointment Booking Agent",
        "docs": "/docs",
        "health": "/health",
    }
