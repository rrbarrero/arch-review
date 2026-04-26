from fastapi import FastAPI

from app.intake.infrastructure.routers.ingest import router as intake_router

app = FastAPI()
app.include_router(intake_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}