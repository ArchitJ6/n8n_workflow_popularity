from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scheduler import setup_scheduler
from config import logger
from contextlib import asynccontextmanager
from services import collector_service
from datetime import datetime
from fastapi.responses import JSONResponse
import asyncio

# Initialize scheduler
setup_scheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        await collector_service.collect_all_workflows()
        logger.info("Initial workflow collection completed")
    except Exception as e:
        logger.error(f"Initial collection failed: {e}")

    yield  # App runs here

    # Shutdown (optional)
    logger.info("App is shutting down.")

# Initialize FastAPI app
app = FastAPI(
    title="N8N Workflow Popularity API",
    description="API to fetch popular n8n workflows across platforms",
    version="1.0.0",
    lifespan=lifespan
)

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return JSONResponse({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

# Workflow endpoints
@app.get("/workflows", tags=["Workflows"])
async def get_workflows(platform: str = None, country: str = None):
    """API endpoint to get workflows with optional filters"""    
    workflows = collector_service.get_workflows_from_db(platform, country)
    
    return JSONResponse({
        'total_count': len(workflows),
        'filters': {
            'platform': platform,
            'country': country
        },
        'workflows': workflows
    })

# Workflow Refresh endpoint
@app.post("/workflows/refresh", tags=["Workflows"])
async def refresh_workflows():
    """API endpoint to manually trigger workflow collection"""    
    try:
        # Run collection in background
        asyncio.create_task(collector_service.collect_all_workflows())
        return JSONResponse({'status': 'Collection started', 'message': 'Workflow data is being updated'})
    except Exception as e:
        return JSONResponse({'error': str(e)}), 500
    
# Workflow Stats endpoint
@app.get("/workflows/stats", tags=["Workflows"])
async def get_workflow_stats():
    """API endpoint to get statistics about collected workflows"""    
    all_workflows = collector_service.get_workflows_from_db()
    
    stats = {
        'total_workflows': len(all_workflows),
        'by_platform': {},
        'by_country': {},
        'last_updated': max([w['last_updated'] for w in all_workflows]) if all_workflows else None
    }
    
    for workflow in all_workflows:
        platform = workflow['platform']
        country = workflow['country']
        
        stats['by_platform'][platform] = stats['by_platform'].get(platform, 0) + 1
        stats['by_country'][country] = stats['by_country'].get(country, 0) + 1
    
    return JSONResponse(stats)
