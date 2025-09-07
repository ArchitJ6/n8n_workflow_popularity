from dataclasses import dataclass, asdict
from typing import Dict

@dataclass
class WorkflowMetrics:
    """Data class for workflow popularity metrics"""
    workflow: str
    platform: str
    popularity_metrics: Dict
    country: str
    last_updated: str = None
    
    def to_dict(self):
        return asdict(self)