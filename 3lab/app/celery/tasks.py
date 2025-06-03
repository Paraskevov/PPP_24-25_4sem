import logging
import random
import time
import redis
import json
from celery import shared_task

logger = logging.getLogger(__name__)
redis_connection = redis.StrictRedis(host='localhost', port=6379, db=0)

def send_parsing_update(user_id: int, update_data: dict):
    """Send parsing progress update via Redis pub/sub."""
    channel = f"parsing_updates:{user_id}"
    redis_connection.publish(channel, json.dumps(update_data))

@shared_task(bind=True)
def start_site_parsing(self, url: str, max_depth: int, user_id: int):
    """Main site parsing task with progress updates."""
    task_id = self.request.id
    
    logger.info(f"Starting parsing task {task_id} for user {user_id}")
    
    # Initial status update
    send_parsing_update(user_id, {
        "status": "started",
        "task_id": task_id,
        "url": url,
        "max_depth": max_depth
    })
    
    total_pages = random.randint(50, 100)
    parsed_pages = 0
    found_links = 0
    
    # Simulate parsing process
    while parsed_pages < total_pages:
        time.sleep(0.5)
        parsed_pages += 1
        found_links += random.randint(1, 3)
        
        send_parsing_update(user_id, {
            "status": "progress",
            "task_id": task_id,
            "progress": (parsed_pages / total_pages) * 100,
            "current_page": f"{url}/page{parsed_pages}",
            "parsed_pages": parsed_pages,
            "total_pages": total_pages,
            "links_found": found_links
        })
    
    # Final result
    result = {
        "status": "completed",
        "task_id": task_id,
        "total_pages": total_pages,
        "total_links": found_links
    }
    
    send_parsing_update(user_id, result)
    return result