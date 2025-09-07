from collectors import YouTubeCollector, ForumCollector, GoogleTrendsCollector
from database import DatabaseManager
from schema import WorkflowMetrics
from typing import Dict, List
from config import logger

class WorkflowCollectorService:
    """Main service that orchestrates all data collection"""
    
    def __init__(self, youtube_api_key: str):
        self.youtube_collector = YouTubeCollector(youtube_api_key)
        self.forum_collector = ForumCollector()
        self.trends_collector = GoogleTrendsCollector()
        self.db_manager = DatabaseManager()
    
    async def collect_all_workflows(self) -> Dict[str, List[WorkflowMetrics]]:
        """Collect workflows from all sources"""
        all_workflows = {
            'YouTube': [],
            'Forum': [],
            'Google': []
        }
        
        countries = ['US', 'IN']
        
        # Collect YouTube data
        for country in countries:
            try:
                youtube_workflows = await self.youtube_collector.search_n8n_workflows(country)
                all_workflows['YouTube'].extend(youtube_workflows)
                logger.info(f"✅ Collected {len(youtube_workflows)} YouTube workflows for {country}")
            except Exception as e:
                logger.error(f"❌ YouTube collection failed for {country}: {e}")
        
        # Collect Forum data
        try:
            forum_workflows = await self.forum_collector.collect_popular_topics()
            all_workflows['Forum'].extend(forum_workflows)
            logger.info(f"✅ Collected {len(forum_workflows)} Forum workflows")
        except Exception as e:
            logger.error(f"❌ Forum collection failed: {e}")
        
        # Collect Google Trends data
        for country in countries:
            try:
                trends_workflows = self.trends_collector.collect_trending_workflows(country)
                all_workflows['Google'].extend(trends_workflows)
                logger.info(f"✅ Collected {len(trends_workflows)} Google Trends workflows for {country}")
            except Exception as e:
                logger.error(f"❌ Google Trends collection failed for {country}: {e}")
        
        # Save to database
        all_workflow_list = []
        for platform_workflows in all_workflows.values():
            all_workflow_list.extend(platform_workflows)
        
        if all_workflow_list:
            self.db_manager.save_workflows(all_workflow_list)
            logger.info(f"💾 Saved {len(all_workflow_list)} total workflows to database")
        else:
            logger.warning("⚠️ No workflows collected from any source!")
        
        return all_workflows
    
    def get_workflows_from_db(self, platform: str = None, country: str = None) -> List[Dict]:
        """Get workflows from database with optional filters"""
        return self.db_manager.get_workflows(platform, country)