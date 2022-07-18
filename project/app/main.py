import logging

from fastapi import FastAPI
from fastapi.routing import APIRoute

from app.api import ping, summaries
from app.db import init_db

log = logging.getLogger("uvicorn")


def custom_generate_unique_id(route: APIRoute):
    return f"{route.tags[0]}-{route.name}"


def create_application() -> FastAPI:
    application = FastAPI(generate_unique_id_function=custom_generate_unique_id)
    application.include_router(ping.router)
    application.include_router(summaries.router, prefix="/summaries")

    return application


app = create_application()


@app.on_event("startup")
async def startup_event():
    log.info("Starting up...")
    init_db(app)


@app.on_event("shutdown")
async def shutdown_event():
    log.info("Shutting down...")
