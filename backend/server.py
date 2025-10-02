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
    
    # Social Media Links
    google_place_id: Optional[str] = None
    tripadvisor_location_id: Optional[str] = None
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
    user = await db.users.find_one({"id": user_id})
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

# Social Media Integration Endpoints
@app.get("/api/social/google-reviews")
async def get_google_reviews(place_id: str, user_id: str = Depends(get_current_user)):
    if not GOOGLE_MAPS_API_KEY:
        return {"error": "Google Maps API key not configured", "reviews": [], "rating": 0}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://maps.googleapis.com/maps/api/place/details/json",
                params={
                    "place_id": place_id,
                    "fields": "rating,user_ratings_total,reviews",
                    "key": GOOGLE_MAPS_API_KEY
                },
                timeout=10.0
            )
            data = response.json()
            
            if data.get("status") == "OK":
                result = data.get("result", {})
                return {
                    "rating": result.get("rating", 0),
                    "total_ratings": result.get("user_ratings_total", 0),
                    "reviews": result.get("reviews", [])[:5]  # Top 5 reviews
                }
            else:
                return {"error": f"Google API error: {data.get('status')}", "reviews": [], "rating": 0}
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
async def get_facebook_likes(page_id: str, user_id: str = Depends(get_current_user)):
    if not FACEBOOK_ACCESS_TOKEN:
        return {"error": "Facebook access token not configured", "likes": 0, "followers": 0}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://graph.facebook.com/v18.0/{page_id}",
                params={
                    "fields": "fan_count,followers_count,name",
                    "access_token": FACEBOOK_ACCESS_TOKEN
                },
                timeout=10.0
            )
            data = response.json()
            return {
                "likes": data.get("fan_count", 0),
                "followers": data.get("followers_count", 0),
                "name": data.get("name", "")
            }
    except Exception as e:
        return {"error": str(e), "likes": 0, "followers": 0}

@app.get("/api/social/instagram-data")
async def get_instagram_data(username: str, user_id: str = Depends(get_current_user)):
    if not INSTAGRAM_ACCESS_TOKEN:
        return {"error": "Instagram access token not configured", "followers": 0, "media_count": 0}
    
    try:
        async with httpx.AsyncClient() as client:
            # Instagram Graph API (requires Business account)
            response = await client.get(
                f"https://graph.instagram.com/me",
                params={
                    "fields": "followers_count,media_count,username",
                    "access_token": INSTAGRAM_ACCESS_TOKEN
                },
                timeout=10.0
            )
            data = response.json()
            return {
                "followers": data.get("followers_count", 0),
                "media_count": data.get("media_count", 0),
                "username": data.get("username", username)
            }
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
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    config = await db.store_configs.find_one({"user_id": user_id})
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    # Get latest sustainability assessment
    sustainability = await db.sustainability_assessments.find_one(
        {"user_id": user_id},
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
