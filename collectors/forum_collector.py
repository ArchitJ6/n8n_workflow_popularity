from config import logger
from datetime import datetime
from typing import Dict, List, Optional
import aiohttp
from schema import WorkflowMetrics

class ForumCollector:
    """Collects n8n workflow data from n8n community forum"""
    
    def __init__(self, base_url: str = "https://community.n8n.io"):
        self.base_url = base_url
    
    async def collect_popular_topics(self) -> List[WorkflowMetrics]:
        """Collect popular topics from n8n forum"""
        workflows = []
        
        async with aiohttp.ClientSession() as session:
            try:
                # Get popular topics
                topics_url = f"{self.base_url}/top.json"
                
                async with session.get(topics_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for topic in data.get('topic_list', {}).get('topics', []):
                            workflow = self._parse_forum_topic(topic)
                            if workflow:
                                workflows.append(workflow)
                
                # Get latest topics for additional coverage
                latest_url = f"{self.base_url}/latest.json"
                
                async with session.get(latest_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for topic in data.get('topic_list', {}).get('topics', []):
                            workflow = self._parse_forum_topic(topic)
                            if workflow and workflow not in workflows:
                                workflows.append(workflow)
            
            except Exception as e:
                logger.error(f"Error fetching forum data: {e}")
        
        return workflows
    
    def _parse_forum_topic(self, topic_data: Dict) -> Optional[WorkflowMetrics]:
        """Parse forum topic into WorkflowMetrics"""
        try:
            title = topic_data.get('title', '')
            views = topic_data.get('views', 0)
            likes = topic_data.get('like_count', 0)
            replies = topic_data.get('reply_count', 0)
            posts_count = topic_data.get('posts_count', 0)
            
            # Filter for workflow-related topics
            workflow_keywords = ['workflow', 'automation', 'integration', 'template', 'tutorial']
            if not any(keyword in title.lower() for keyword in workflow_keywords):
                return None
            
            # Skip low-engagement topics
            if views < 50:
                return None
            
            return WorkflowMetrics(
                workflow=title,
                platform="Forum",
                popularity_metrics={
                    "views": views,
                    "likes": likes,
                    "replies": replies,
                    "posts_count": posts_count,
                    "engagement_score": (likes * 2 + replies * 3) / max(views, 1)
                },
                country="Global",  # Forum is global
                last_updated=datetime.now().isoformat()
            )
        
        except Exception as e:
            logger.error(f"Error parsing forum topic: {e}")
            return None