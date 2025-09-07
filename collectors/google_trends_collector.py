from config import logger
from datetime import datetime
from typing import List
from schema import WorkflowMetrics
from pytrends.request import TrendReq
import time
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import requests

class GoogleTrendsCollector:
    """Collects n8n workflow popularity data from Google Trends"""
    
    def __init__(self):
        # Retry config
        # retries = 3
        # backoff_factor = 0.3
        # retry_strategy = Retry(
        #     total=retries,
        #     read=retries,
        #     connect=retries,
        #     backoff_factor=backoff_factor,
        #     status_forcelist=[429, 500, 502, 503, 504],
        #     allowed_methods=frozenset(['GET', 'POST'])
        # )

        # # Session with retry
        # adapter = HTTPAdapter(max_retries=retry_strategy)
        # session = requests.Session()
        # session.mount("https://", adapter)
        # session.mount("http://", adapter)
        self.pytrends = TrendReq(
            hl='en-US',
            tz=360,
            timeout=(10, 25),
            # requests_args={'verify': False},
            retries=2,
            backoff_factor=0.5
        )
        # self.pytrends._requests_session = session

    def collect_trending_workflows(self, country: str = "US") -> List[WorkflowMetrics]:
        """Collect trending n8n workflows from Google Trends"""
        workflows = []
        
        # Common n8n workflow keywords
        workflow_keywords = [
            "n8n slack automation",
            "n8n google sheets integration",
            "n8n email automation",
            "n8n webhook workflow",
            "n8n database automation",
            # "n8n api integration",
            # "n8n discord bot",
            # "n8n twitter automation",
            # "n8n notion integration",
            # "n8n airtable workflow",
            # "n8n telegram bot",
            # "n8n shopify automation",
            # "n8n wordpress integration",
            # "n8n github automation",
            # "n8n jira integration"
        ]
        
        # Process keywords in batches (Google Trends API limitation)
        batch_size = 1
        for i in range(0, len(workflow_keywords), batch_size):
            batch = workflow_keywords[i:i + batch_size]
            
            try:
                # Set up trends request
                geo_code = country if country in ['US', 'IN'] else 'US'
                self.pytrends.build_payload(
                    kw_list=batch,
                    cat=0, 
                    timeframe='today 1-m',  # Last 1 month
                    geo=geo_code,
                    gprop=''
                )
                
                # Get interest over time
                interest_data = self.pytrends.interest_over_time()
                
                if not interest_data.empty:
                    for keyword in batch:
                        if keyword in interest_data.columns:
                            avg_interest = interest_data[keyword].mean()
                            recent_trend = self._calculate_trend_change(interest_data[keyword])
                            
                            if avg_interest > 5:  # Only include keywords with meaningful search volume
                                workflow = WorkflowMetrics(
                                    workflow=keyword.replace("n8n ", "").title(),
                                    platform="Google",
                                    popularity_metrics={
                                        "average_interest": round(avg_interest, 2),
                                        "trend_change_percent": round(recent_trend, 2),
                                        "peak_interest": int(interest_data[keyword].max()),
                                        "search_consistency": round(interest_data[keyword].std(), 2)
                                    },
                                    country=country,
                                    last_updated=datetime.now().isoformat()
                                )
                                workflows.append(workflow)
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error fetching Google Trends data for batch {batch}: {e}")
                time.sleep(2)  # Longer wait on error
        
        return workflows
    
    def _calculate_trend_change(self, series) -> float:
        """Calculate trend change percentage over the time period"""
        if len(series) < 4:
            return 0.0
        
        # Compare last quarter to previous quarter
        quarter_size = len(series) // 4
        recent_avg = series[-quarter_size:].mean()
        previous_avg = series[-2*quarter_size:-quarter_size].mean()
        
        if previous_avg > 0:
            return ((recent_avg - previous_avg) / previous_avg) * 100
        return 0.0