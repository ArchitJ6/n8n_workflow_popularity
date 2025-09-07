from config import logger
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
import aiohttp
from schema import WorkflowMetrics

class YouTubeCollector:
    """Collects n8n workflow data from YouTube"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/youtube/v3"
    
    async def search_n8n_workflows(self, country: str = "US") -> List[WorkflowMetrics]:
        """Search for n8n workflow videos on YouTube"""
        workflows = []
        
        search_queries = [
            "n8n workflow automation",
            "n8n tutorial workflow",
            "n8n integration workflow",
            "n8n slack automation",
            "n8n google sheets workflow",
            "n8n email automation",
            "n8n webhook workflow",
            "n8n database automation",
            "n8n api integration",
            "n8n zapier alternative"
        ]
        
        async with aiohttp.ClientSession() as session:
            for query in search_queries:
                try:
                    # Search for videos
                    search_url = f"{self.base_url}/search"
                    search_params = {
                        'key': self.api_key,
                        'q': query,
                        'part': 'snippet',
                        'type': 'video',
                        'maxResults': 25,
                        'regionCode': country,
                        'order': 'relevance'
                    }
                    
                    async with session.get(search_url, params=search_params) as response:
                        if response.status == 200:
                            search_data = await response.json()
                            video_ids = [item['id']['videoId'] for item in search_data.get('items', [])]
                            
                            if video_ids:
                                # Get video statistics
                                stats_url = f"{self.base_url}/videos"
                                stats_params = {
                                    'key': self.api_key,
                                    'id': ','.join(video_ids),
                                    'part': 'statistics,snippet'
                                }
                                
                                async with session.get(stats_url, params=stats_params) as stats_response:
                                    if stats_response.status == 200:
                                        stats_data = await stats_response.json()
                                        
                                        for video in stats_data.get('items', []):
                                            workflow = self._parse_video_data(video, country)
                                            if workflow:
                                                workflows.append(workflow)
                        
                        # Rate limiting
                        await asyncio.sleep(0.1)
                
                except Exception as e:
                    logger.error(f"Error fetching YouTube data for query '{query}': {e}")
        
        return workflows
    
    def _parse_video_data(self, video_data: Dict, country: str) -> Optional[WorkflowMetrics]:
        """Parse video data into WorkflowMetrics"""
        try:
            snippet = video_data.get('snippet', {})
            stats = video_data.get('statistics', {})
            
            views = int(stats.get('viewCount', 0))
            likes = int(stats.get('likeCount', 0))
            comments = int(stats.get('commentCount', 0))
            
            # Skip videos with low engagement
            if views < 100:
                return None
            
            title = snippet.get('title', '')
            
            # Calculate engagement ratios
            like_to_view_ratio = likes / views if views > 0 else 0
            comment_to_view_ratio = comments / views if views > 0 else 0
            
            return WorkflowMetrics(
                workflow=title,
                platform="YouTube",
                popularity_metrics={
                    "views": views,
                    "likes": likes,
                    "comments": comments,
                    "like_to_view_ratio": round(like_to_view_ratio, 4),
                    "comment_to_view_ratio": round(comment_to_view_ratio, 4)
                },
                country=country,
                last_updated=datetime.now().isoformat()
            )
        
        except Exception as e:
            logger.error(f"Error parsing video data: {e}")
            return None