import json
import sqlite3
from datetime import datetime
from typing import Dict, List
from schema import WorkflowMetrics
from config import logger

class DatabaseManager:
    """Manages SQLite database operations"""
    
    def __init__(self, db_path: str = "data/workflows.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workflows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow TEXT NOT NULL,
                platform TEXT NOT NULL,
                popularity_metrics TEXT NOT NULL,
                country TEXT NOT NULL,
                last_updated TEXT NOT NULL,
                UNIQUE(workflow, platform, country)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_workflows(self, workflows: List[WorkflowMetrics]):
        """Save or update workflows in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for workflow in workflows:
            cursor.execute('''
                INSERT OR REPLACE INTO workflows 
                (workflow, platform, popularity_metrics, country, last_updated)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                workflow.workflow,
                workflow.platform,
                json.dumps(workflow.popularity_metrics),
                workflow.country,
                workflow.last_updated or datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
        logger.info(f"Saved {len(workflows)} workflows to database")
    
    def get_workflows(self, platform: str = None, country: str = None) -> List[Dict]:
        """Retrieve workflows from database with optional filters"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM workflows"
        params = []
        
        if platform or country:
            query += " WHERE "
            conditions = []
            if platform:
                conditions.append("LOWER(platform) = LOWER(?)")
                params.append(platform)
            if country:
                conditions.append("LOWER(country) = LOWER(?)")
                params.append(country)
            query += " AND ".join(conditions)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            results.append({
                'workflow': row[1],
                'platform': row[2],
                'popularity_metrics': json.loads(row[3]),
                'country': row[4],
                'last_updated': row[5]
            })
        
        return results