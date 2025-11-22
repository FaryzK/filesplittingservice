"""Progress tracking for inference operations."""
from typing import Dict, Optional
import time
import uuid


class ProgressTracker:
    """Thread-safe progress tracker for inference operations."""
    
    _instances: Dict[str, Dict] = {}
    
    @classmethod
    def create_job(cls, job_id: Optional[str] = None) -> str:
        """Create a new progress tracking job."""
        if job_id is None:
            job_id = str(uuid.uuid4())
        
        cls._instances[job_id] = {
            "status": "initializing",
            "current_page": 0,
            "total_pages": 0,
            "processed_pages": [],
            "identified_documents": [],
            "progress_percentage": 0,
            "message": "Initializing...",
            "start_time": time.time(),
            "error": None
        }
        return job_id
    
    @classmethod
    def update_progress(
        cls,
        job_id: str,
        status: str = None,
        current_page: int = None,
        total_pages: int = None,
        message: str = None,
        page_info: Dict = None,
        identified_document: Dict = None
    ):
        """Update progress for a job."""
        if job_id not in cls._instances:
            print(f"Warning: Job {job_id} not found in progress tracker")
            return
        
        job = cls._instances[job_id]
        
        if status:
            job["status"] = status
        if current_page is not None:
            job["current_page"] = current_page
        if total_pages is not None:
            job["total_pages"] = total_pages
        if message:
            job["message"] = message
        if page_info:
            if "processed_pages" not in job:
                job["processed_pages"] = []
            job["processed_pages"].append(page_info)
        if identified_document:
            if "identified_documents" not in job:
                job["identified_documents"] = []
            job["identified_documents"].append(identified_document)
        
        # Calculate progress percentage
        if job["total_pages"] > 0:
            job["progress_percentage"] = int((job["current_page"] / job["total_pages"]) * 100)
        else:
            job["progress_percentage"] = 0
        
        # Debug log
        print(f"Progress update for job {job_id}: {job['status']} - {job['message']} ({job['progress_percentage']}%)")
    
    @classmethod
    def get_progress(cls, job_id: str) -> Optional[Dict]:
        """Get current progress for a job."""
        return cls._instances.get(job_id)
    
    @classmethod
    def complete_job(cls, job_id: str, result: Dict = None):
        """Mark a job as complete."""
        if job_id not in cls._instances:
            return
        
        job = cls._instances[job_id]
        job["status"] = "completed"
        job["progress_percentage"] = 100
        job["message"] = "Processing complete!"
        if result:
            job["result"] = result
        job["end_time"] = time.time()
        job["duration"] = job["end_time"] - job["start_time"]
    
    @classmethod
    def fail_job(cls, job_id: str, error: str):
        """Mark a job as failed."""
        if job_id not in cls._instances:
            return
        
        job = cls._instances[job_id]
        job["status"] = "failed"
        job["error"] = error
        job["message"] = f"Error: {error}"
        job["end_time"] = time.time()
        job["duration"] = job["end_time"] - job["start_time"]
    
    @classmethod
    def cleanup(cls, job_id: str):
        """Remove a job from tracking (optional cleanup)."""
        cls._instances.pop(job_id, None)

