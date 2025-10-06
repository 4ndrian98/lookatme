from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
import jwt
import os
import uuid
import httpx
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Look@Me CMS API")

# CORS Configuration
origins = os.environ.get('CORS_ORIGINS', '*').split(',')
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database
client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
db = client[os.environ.get('DB_NAME', 'lookatme_cms')]

# Security
import hashlib
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
security = HTTPBearer()
JWT_SECRET = os.environ.get('JWT_SECRET', 'default-secret-key')
JWT_ALGORITHM = "HS256"

# Environment Variables
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', '')
TRIPADVISOR_API_KEY = os.environ.get('TRIPADVISOR_API_KEY', '')
FACEBOOK_ACCESS_TOKEN = os.environ.get('FACEBOOK_ACCESS_TOKEN', '')
INSTAGRAM_ACCESS_TOKEN = os.environ.get('INSTAGRAM_ACCESS_TOKEN', '')
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY', '')
BRIGHTDATA_API_TOKEN = os.environ.get('BRIGHTDATA_API_TOKEN', '')

# Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    business_name: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    business_name: str

class UserLogin(BaseModel):
    username: str
    password: str

class StoreConfig(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    logo_url: Optional[str] = None
    business_description: Optional[str] = None
    mission_statement: Optional[str] = None
    
    # Visibility toggles
    show_social_likes: bool = True
    show_satisfied_customers: bool = True
    show_sustainability_index: bool = True
    show_environmental_impact: bool = True
    show_recognitions: bool = True
    show_amenities: bool = True
    show_additional_services: bool = True
    show_customer_satisfaction_chart: bool = True
    
    # Services
    amenities: List[str] = []
    additional_services: List[str] = []
    
    # Recognitions
    recognitions: List[Dict[str, str]] = []  # [{"name": "cert_name", "icon_url": "..."}]
    
    # Social Media Links (URLs for BrightData)
    instagram_url: Optional[str] = None
    facebook_url: Optional[str] = None
    google_maps_url: Optional[str] = None
    tripadvisor_location_id: Optional[str] = None  # Still using direct API
    
    # Legacy fields (for backwards compatibility)
    google_place_id: Optional[str] = None
    facebook_page_id: Optional[str] = None
    instagram_username: Optional[str] = None
    
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class SustainabilityRequest(BaseModel):
    business_name: str
    business_type: str
    description: Optional[str] = None

# Helper Functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Auth Endpoints
@app.post("/api/auth/register")
async def register(user_data: UserRegister):
    # Check if user exists
    existing_user = await db.users.find_one({"username": user_data.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    existing_email = await db.users.find_one({"email": user_data.email})
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # Create user
    user = User(
        username=user_data.username,
        email=user_data.email,
        business_name=user_data.business_name
    )
    
    user_dict = user.dict()
    user_dict["password_hash"] = pwd_context.hash(user_data.password)
    
    await db.users.insert_one(user_dict)
    
    # Create default store config
    default_config = StoreConfig(user_id=user.id)
    await db.store_configs.insert_one(default_config.dict())
    
    # Generate token
    token = create_access_token({"user_id": user.id})
    
    return {
        "message": "User registered successfully",
        "token": token,
        "user": {"id": user.id, "username": user.username, "email": user.email, "business_name": user.business_name}
    }

@app.post("/api/auth/login")
async def login(credentials: UserLogin):
    user = await db.users.find_one({"username": credentials.username})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not pwd_context.verify(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"user_id": user["id"]})
    
    return {
        "message": "Login successful",
        "token": token,
        "user": {"id": user["id"], "username": user["username"], "email": user["email"], "business_name": user["business_name"]}
    }

@app.get("/api/auth/me")
async def get_me(user_id: str = Depends(get_current_user)):
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"id": user["id"], "username": user["username"], "email": user["email"], "business_name": user["business_name"]}

# Store Configuration Endpoints
@app.get("/api/store/config")
async def get_store_config(user_id: str = Depends(get_current_user)):
    config = await db.store_configs.find_one({"user_id": user_id}, {"_id": 0})
    if not config:
        # Create default config if not exists
        default_config = StoreConfig(user_id=user_id)
        await db.store_configs.insert_one(default_config.dict())
        return default_config.dict()
    return config

@app.put("/api/store/config")
async def update_store_config(config_update: Dict[str, Any], user_id: str = Depends(get_current_user)):
    config_update["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    result = await db.store_configs.update_one(
        {"user_id": user_id},
        {"$set": config_update}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    updated_config = await db.store_configs.find_one({"user_id": user_id}, {"_id": 0})
    return {"message": "Configuration updated successfully", "config": updated_config}

# Social Media Integration Endpoints (via BrightData)
from brightdata_integration import get_social_data_via_brightdata, BrightDataClient

@app.get("/api/social/google-reviews")
async def get_google_reviews(place_url: str, user_id: str = Depends(get_current_user)):
    """
    Get Google Maps reviews via BrightData
    Args:
        place_url: Full Google Maps URL (e.g., https://www.google.com/maps/place/...)
    """
    if not BRIGHTDATA_API_TOKEN:
        return {"error": "BrightData API token not configured", "reviews": [], "rating": 0}
    
    try:
        result = await get_social_data_via_brightdata(
            platform="googlemaps",
            url=place_url,
            api_token=BRIGHTDATA_API_TOKEN,
            params={"days_limit": 30},
            wait_for_results=False  # Return job_id immediately
        )
        
        if result.get("status") == "job_created":
            # Store job for later polling
            await db.brightdata_jobs.insert_one({
                "user_id": user_id,
                "job_id": result["job_id"],
                "platform": "googlemaps",
                "url": place_url,
                "status": "running",
                "created_at": datetime.now(timezone.utc).isoformat()
            })
            return {
                "message": "Crawl job started. Check status with job_id.",
                "job_id": result["job_id"],
                "status": "running"
            }
        else:
            return result
    except Exception as e:
        return {"error": str(e), "reviews": [], "rating": 0}

@app.get("/api/social/tripadvisor-reviews")
async def get_tripadvisor_reviews(location_id: str, user_id: str = Depends(get_current_user)):
    if not TRIPADVISOR_API_KEY:
        return {"error": "TripAdvisor API key not configured", "reviews": [], "rating": 0}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.content.tripadvisor.com/api/v1/location/{location_id}/reviews",
                headers={"accept": "application/json"},
                params={"key": TRIPADVISOR_API_KEY, "language": "en"},
                timeout=10.0
            )
            data = response.json()
            return {"reviews": data.get("data", [])[:5], "rating": 0}  # TripAdvisor API structure
    except Exception as e:
        return {"error": str(e), "reviews": [], "rating": 0}

@app.get("/api/social/facebook-likes")
async def get_facebook_likes(page_url: str, user_id: str = Depends(get_current_user)):
    """
    Get Facebook page data via BrightData
    Args:
        page_url: Full Facebook page URL (e.g., https://www.facebook.com/yourpage)
    """
    if not BRIGHTDATA_API_TOKEN:
        return {"error": "BrightData API token not configured", "likes": 0, "followers": 0}
    
    try:
        result = await get_social_data_via_brightdata(
            platform="facebook",
            url=page_url,
            api_token=BRIGHTDATA_API_TOKEN,
            params={"num_of_reviews": 50},
            wait_for_results=False
        )
        
        if result.get("status") == "job_created":
            await db.brightdata_jobs.insert_one({
                "user_id": user_id,
                "job_id": result["job_id"],
                "platform": "facebook",
                "url": page_url,
                "status": "running",
                "created_at": datetime.now(timezone.utc).isoformat()
            })
            return {
                "message": "Crawl job started. Check status with job_id.",
                "job_id": result["job_id"],
                "status": "running"
            }
        else:
            return result
    except Exception as e:
        return {"error": str(e), "likes": 0, "followers": 0}

@app.get("/api/social/instagram-data")
async def get_instagram_data(profile_url: str, user_id: str = Depends(get_current_user)):
    """
    Get Instagram profile data via BrightData
    Args:
        profile_url: Full Instagram profile URL (e.g., https://www.instagram.com/username/)
    """
    if not BRIGHTDATA_API_TOKEN:
        return {"error": "BrightData API token not configured", "followers": 0, "media_count": 0}
    
    try:
        result = await get_social_data_via_brightdata(
            platform="instagram",
            url=profile_url,
            api_token=BRIGHTDATA_API_TOKEN,
            params={},
            wait_for_results=False
        )
        
        if result.get("status") == "job_created":
            await db.brightdata_jobs.insert_one({
                "user_id": user_id,
                "job_id": result["job_id"],
                "platform": "instagram",
                "url": profile_url,
                "status": "running",
                "created_at": datetime.now(timezone.utc).isoformat()
            })
            return {
                "message": "Crawl job started. Check status with job_id.",
                "job_id": result["job_id"],
                "status": "running"
            }
        else:
            return result
    except Exception as e:
        return {"error": str(e), "followers": 0, "media_count": 0}

# BrightData Job Management Endpoints
@app.get("/api/brightdata/job-status/{job_id}")
async def get_brightdata_job_status(job_id: str, user_id: str = Depends(get_current_user)):
    """Check the status of a BrightData crawl job"""
    if not BRIGHTDATA_API_TOKEN:
        raise HTTPException(status_code=500, detail="BrightData API token not configured")
    
    try:
        client = BrightDataClient(BRIGHTDATA_API_TOKEN)
        status = await client.check_job_status(job_id)
        
        # Update job status in database
        await db.brightdata_jobs.update_one(
            {"job_id": job_id, "user_id": user_id},
            {"$set": {"status": status.get("status"), "progress": status.get("progress", 0)}}
        )
        
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/brightdata/job-results/{job_id}")
async def get_brightdata_job_results(job_id: str, user_id: str = Depends(get_current_user)):
    """Get results from a completed BrightData job"""
    if not BRIGHTDATA_API_TOKEN:
        raise HTTPException(status_code=500, detail="BrightData API token not configured")
    
    try:
        # Check if job belongs to user
        job = await db.brightdata_jobs.find_one({"job_id": job_id, "user_id": user_id}, {"_id": 0})
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        client = BrightDataClient(BRIGHTDATA_API_TOKEN)
        result = await client.get_results(job_id)
        
        if result.get("status") == "completed":
            # Parse data based on platform
            platform = job.get("platform")
            raw_data = result.get("data", [])
            
            from brightdata_integration import PARSERS
            parser = PARSERS.get(platform)
            
            if parser:
                parsed_data = parser(raw_data)
            else:
                parsed_data = raw_data
            
            # Update job status and store results
            await db.brightdata_jobs.update_one(
                {"job_id": job_id},
                {"$set": {
                    "status": "completed",
                    "results": parsed_data,
                    "completed_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            
            return {
                "status": "success",
                "platform": platform,
                "data": parsed_data,
                "job_id": job_id
            }
        else:
            return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/brightdata/my-jobs")
async def get_my_brightdata_jobs(user_id: str = Depends(get_current_user)):
    """Get all BrightData jobs for the current user"""
    try:
        jobs = await db.brightdata_jobs.find(
            {"user_id": user_id},
            {"_id": 0}
        ).sort("created_at", -1).limit(20).to_list(length=20)
        
        return {"jobs": jobs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/brightdata/refresh-all-social")
async def refresh_all_social_data(user_id: str = Depends(get_current_user)):
    """
    Trigger crawl jobs for all configured social platforms
    Returns job_ids for tracking
    """
    if not BRIGHTDATA_API_TOKEN:
        raise HTTPException(status_code=500, detail="BrightData API token not configured")
    
    try:
        # Get user's store config
        config = await db.store_configs.find_one({"user_id": user_id}, {"_id": 0})
        if not config:
            raise HTTPException(status_code=404, detail="Store configuration not found")
        
        jobs = []
        
        # Trigger Instagram crawl
        if config.get("instagram_url"):
            result = await get_social_data_via_brightdata(
                platform="instagram",
                url=config["instagram_url"],
                api_token=BRIGHTDATA_API_TOKEN,
                wait_for_results=False
            )
            if result.get("status") == "job_created":
                jobs.append({"platform": "instagram", "job_id": result["job_id"]})
        
        # Trigger Facebook crawl
        if config.get("facebook_url"):
            result = await get_social_data_via_brightdata(
                platform="facebook",
                url=config["facebook_url"],
                api_token=BRIGHTDATA_API_TOKEN,
                params={"num_of_reviews": 50},
                wait_for_results=False
            )
            if result.get("status") == "job_created":
                jobs.append({"platform": "facebook", "job_id": result["job_id"]})
        
        # Trigger Google Maps crawl
        if config.get("google_maps_url"):
            result = await get_social_data_via_brightdata(
                platform="googlemaps",
                url=config["google_maps_url"],
                api_token=BRIGHTDATA_API_TOKEN,
                params={"days_limit": 30},
                wait_for_results=False
            )
            if result.get("status") == "job_created":
                jobs.append({"platform": "googlemaps", "job_id": result["job_id"]})
        
        return {
            "message": f"Started {len(jobs)} crawl jobs",
            "jobs": jobs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        return {"error": str(e), "followers": 0, "media_count": 0}

# AI - Sustainability Index Calculation
@app.post("/api/sustainability/calculate")
async def calculate_sustainability(request: SustainabilityRequest, user_id: str = Depends(get_current_user)):
    if not GEMINI_API_KEY and not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="Gemini API key not configured")
    
    try:
        # Use Gemini AI to calculate sustainability index
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        api_key = EMERGENT_LLM_KEY if EMERGENT_LLM_KEY else GEMINI_API_KEY
        
        chat = LlmChat(
            api_key=api_key,
            session_id=f"sustainability-{user_id}-{uuid.uuid4()}",
            system_message="You are a sustainability expert. Analyze businesses and provide sustainability scores."
        ).with_model("gemini", "gemini-2.0-flash")
        
        prompt = f"""
Analyze the following business and provide a sustainability assessment:

Business Name: {request.business_name}
Business Type: {request.business_type}
Description: {request.description or 'Not provided'}

Provide a JSON response with the following structure:
{{
  "sustainability_index": <number 0-100>,
  "environmental_score": <number 0-100>,
  "social_score": <number 0-100>,
  "recommendations": [<list of 3-5 recommendations>],
  "strengths": [<list of 2-3 strengths>],
  "areas_for_improvement": [<list of 2-3 areas>]
}}

Be realistic and provide actionable insights.
"""
        
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        # Parse JSON from response
        import json
        import re
        
        # Extract JSON from markdown code blocks if present
        json_match = re.search(r'```(?:json)?\s*({.*?})\s*```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find JSON object directly
            json_match = re.search(r'{.*}', response, re.DOTALL)
            json_str = json_match.group(0) if json_match else response
        
        result = json.loads(json_str)
        
        # Save to database
        sustainability_data = {
            "user_id": user_id,
            "business_name": request.business_name,
            "business_type": request.business_type,
            "result": result,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.sustainability_assessments.insert_one(sustainability_data)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating sustainability: {str(e)}")

# Display Preview Endpoint
@app.get("/api/display/{user_id}")
async def get_display_data(user_id: str):
    """Public endpoint to get display data for storefront"""
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    config = await db.store_configs.find_one({"user_id": user_id}, {"_id": 0})
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    # Get latest sustainability assessment
    sustainability = await db.sustainability_assessments.find_one(
        {"user_id": user_id},
        {"_id": 0},
        sort=[("created_at", -1)]
    )
    
    # Aggregate social data if configured
    social_data = {}
    
    if config.get("google_place_id"):
        google_data = await get_google_reviews(config["google_place_id"], user_id)
        social_data["google"] = google_data
    
    if config.get("facebook_page_id"):
        fb_data = await get_facebook_likes(config["facebook_page_id"], user_id)
        social_data["facebook"] = fb_data
    
    if config.get("instagram_username"):
        ig_data = await get_instagram_data(config["instagram_username"], user_id)
        social_data["instagram"] = ig_data
    
    return {
        "business_name": user["business_name"],
        "config": config,
        "sustainability": sustainability.get("result") if sustainability else None,
        "social_data": social_data
    }

# Health check
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}
