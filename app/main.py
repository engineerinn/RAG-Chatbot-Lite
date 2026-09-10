import logging
import uvicorn
from fastapi import FastAPI
from app.config.system_cnfg import settings as SETTINGS
from contextlib import asynccontextmanager
from app.api.v1.routing_controller import RoutingController
from fastapi.middleware.cors import CORSMiddleware
from app.config.logger_cnfg import setup_logging
#from lingua import Language, LanguageDetectorBuilder

setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    #start
    logger.info("Starting the Chatbot Service.")

    yield

    logger.info("Stopping the Chatbot Service.")

app = FastAPI(title="RAG Chatbot Lite", lifespan=lifespan)

search_controller = RoutingController()

app.include_router(search_controller.router, prefix="/api/v1")

#CORS Setting
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

if __name__ == "__main__":

    uvicorn.run(
        "main:app",
        host=SETTINGS.APP_HOST,
        port=SETTINGS.APP_PORT,
        reload=SETTINGS.APP_RELOAD,
    )
