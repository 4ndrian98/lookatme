"""
BrightData Integration Module for Look@Me CMS
Handles data collection from Instagram, Facebook, and Google Maps via BrightData API
"""

import httpx
import asyncio
from typing import Dict, Optional, List, Any
from datetime import datetime
import os

class BrightDataClient:
    """Client for interacting with BrightData API"""
    
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.base_url = "https://api.brightdata.com/datasets/v3"
        self.dataset_ids = {
            "instagram": "gd_l7q7dkf244hwjntr0",  # Instagram dataset
            "facebook": "gd_lvhf8tq8ky28b3tbz",    # Facebook dataset  
            "googlemaps": "gd_l7q7dkf244hwjku40"   # Google Maps dataset
        }
        
    async def trigger_crawl(self, platform: str, urls: List[str], params: Optional[Dict] = None) -> Dict:
        """
        Trigger a crawl job for a specific platform
        
        Args:
            platform: One of 'instagram', 'facebook', 'googlemaps'
            urls: List of URLs to crawl
            params: Platform-specific parameters
            
        Returns:
            Dict with job_id and status
        """
        if platform not in self.dataset_ids:
            raise ValueError(f"Unsupported platform: {platform}. Must be one of {list(self.dataset_ids.keys())}")
        
        dataset_id = self.dataset_ids[platform]
        
        # Prepare payload based on platform
        payload = []
        for url in urls:
            entry = {"url": url}
            if params:
                entry.update(params)
            payload.append(entry)
        
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/trigger",
                    params={"dataset_id": dataset_id},
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()
                
                return {
                    "job_id": data.get("snapshot_id"),
                    "status": "running",
                    "platform": platform,
                    "urls": urls,
                    "created_at": datetime.utcnow().isoformat()
                }
        except httpx.HTTPStatusError as e:
            return {
                "error": f"HTTP error {e.response.status_code}: {e.response.text}",
                "status": "failed"
            }
        except Exception as e:
            return {
                "error": str(e),
                "status": "failed"
            }
    
    async def check_job_status(self, job_id: str) -> Dict:
        """
        Check the status of a crawl job
        
        Args:
            job_id: The snapshot_id returned from trigger_crawl
            
        Returns:
            Dict with status information
        """
        headers = {
            "Authorization": f"Bearer {self.api_token}"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/progress/{job_id}",
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()
                
                return {
                    "job_id": job_id,
                    "status": data.get("status", "unknown"),
                    "progress": data.get("progress", 0),
                    "total_records": data.get("total_records", 0)
                }
        except Exception as e:
            return {
                "job_id": job_id,
                "status": "error",
                "error": str(e)
            }
    
    async def get_results(self, job_id: str) -> Dict:
        """
        Retrieve results from a completed crawl job
        
        Args:
            job_id: The snapshot_id returned from trigger_crawl
            
        Returns:
            Dict with crawled data
        """
        headers = {
            "Authorization": f"Bearer {self.api_token}"
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(
                    f"{self.base_url}/snapshot/{job_id}",
                    params={"format": "json"},
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()
                
                return {
                    "job_id": job_id,
                    "status": "completed",
                    "data": data,
                    "retrieved_at": datetime.utcnow().isoformat()
                }
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {
                    "job_id": job_id,
                    "status": "not_found",
                    "error": "Job not found or not yet completed"
                }
            return {
                "job_id": job_id,
                "status": "error",
                "error": f"HTTP {e.response.status_code}: {e.response.text}"
            }
        except Exception as e:
            return {
                "job_id": job_id,
                "status": "error",
                "error": str(e)
            }
    
    async def wait_for_completion(self, job_id: str, max_wait: int = 300, poll_interval: int = 10) -> Dict:
        """
        Wait for a job to complete and return results
        
        Args:
            job_id: The snapshot_id to wait for
            max_wait: Maximum wait time in seconds
            poll_interval: How often to check status in seconds
            
        Returns:
            Dict with final results or error
        """
        elapsed = 0
        
        while elapsed < max_wait:
            status = await self.check_job_status(job_id)
            
            if status.get("status") == "ready":
                return await self.get_results(job_id)
            elif status.get("status") in ["failed", "error"]:
                return status
            
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval
        
        return {
            "job_id": job_id,
            "status": "timeout",
            "error": f"Job did not complete within {max_wait} seconds"
        }


def parse_instagram_data(raw_data: List[Dict]) -> Dict:
    """Parse Instagram crawl results"""
    if not raw_data or len(raw_data) == 0:
        return {"followers": 0, "posts": 0, "error": "No data returned"}
    
    item = raw_data[0]
    return {
        "followers": item.get("followers_count", 0),
        "posts": item.get("posts_count", 0),
        "username": item.get("username", ""),
        "profile_url": item.get("url", "")
    }


def parse_facebook_data(raw_data: List[Dict]) -> Dict:
    """Parse Facebook crawl results"""
    if not raw_data or len(raw_data) == 0:
        return {"fans": 0, "reviews_count": 0, "rating": 0, "error": "No data returned"}
    
    item = raw_data[0]
    return {
        "fans": item.get("fans_count", 0),
        "reviews_count": item.get("reviews_count", 0),
        "rating": item.get("rating", 0),
        "page_name": item.get("name", "")
    }


def parse_googlemaps_data(raw_data: List[Dict]) -> Dict:
    """Parse Google Maps crawl results"""
    if not raw_data or len(raw_data) == 0:
        return {"reviews_count": 0, "rating": 0, "error": "No data returned"}
    
    item = raw_data[0]
    return {
        "reviews_count": item.get("reviews_count", 0),
        "rating": item.get("rating", 0),
        "place_name": item.get("name", ""),
        "address": item.get("address", "")
    }


# Parser mapping
PARSERS = {
    "instagram": parse_instagram_data,
    "facebook": parse_facebook_data,
    "googlemaps": parse_googlemaps_data
}


async def get_social_data_via_brightdata(
    platform: str,
    url: str,
    api_token: str,
    params: Optional[Dict] = None,
    wait_for_results: bool = False
) -> Dict:
    """
    High-level function to get social data via BrightData
    
    Args:
        platform: 'instagram', 'facebook', or 'googlemaps'
        url: URL to crawl
        api_token: BrightData API token
        params: Platform-specific parameters
        wait_for_results: If True, wait for job completion and return data
        
    Returns:
        Dict with either job_id (if not waiting) or parsed data (if waiting)
    """
    client = BrightDataClient(api_token)
    
    # Trigger the crawl
    trigger_result = await client.trigger_crawl(platform, [url], params)
    
    if trigger_result.get("status") == "failed":
        return trigger_result
    
    job_id = trigger_result.get("job_id")
    
    if not wait_for_results:
        return {
            "status": "job_created",
            "job_id": job_id,
            "message": f"Crawl job created for {platform}. Check status with job_id."
        }
    
    # Wait for completion
    result = await client.wait_for_completion(job_id)
    
    if result.get("status") != "completed":
        return result
    
    # Parse the data
    raw_data = result.get("data", [])
    parser = PARSERS.get(platform)
    
    if parser:
        parsed = parser(raw_data)
        return {
            "status": "success",
            "platform": platform,
            "data": parsed,
            "job_id": job_id
        }
    else:
        return {
            "status": "success",
            "platform": platform,
            "data": raw_data,
            "job_id": job_id
        }
