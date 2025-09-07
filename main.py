import uvicorn
from config import DEVELOPMENT_MODE, logger

if __name__ == "__main__":
    if DEVELOPMENT_MODE:
        logger.info("Starting in development mode...")
    else:
        logger.info("Starting in production mode...")
    uvicorn.run("api.routes:app", host="0.0.0.0", port=8000, reload=DEVELOPMENT_MODE, log_level="info")