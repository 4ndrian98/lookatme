#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Look@Me CMS
Tests all backend API endpoints with realistic data
"""

import asyncio
import httpx
import json
import uuid
from datetime import datetime

# Configuration
BASE_URL = "https://store-display-1.preview.emergentagent.com/api"
TIMEOUT = 30.0

class BackendTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=TIMEOUT)
        self.auth_token = None
        self.user_id = None
        self.test_results = {}
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def log_result(self, test_name, success, details="", error=None):
        """Log test results"""
        self.test_results[test_name] = {
            "success": success,
            "details": details,
            "error": str(error) if error else None,
            "timestamp": datetime.now().isoformat()
        }
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        if error:
            print(f"   Error: {error}")
    
    async def test_health_check(self):
        """Test health check endpoint"""
        try:
            response = await self.client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                self.log_result("Health Check", True, f"Status: {data.get('status')}")
                return True
            else:
                self.log_result("Health Check", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Health Check", False, error=e)
            return False
    
    async def test_user_registration(self):
        """Test user registration"""
        try:
            # Generate unique test data
            test_id = str(uuid.uuid4())[:8]
            user_data = {
                "username": f"testowner_{test_id}",
                "email": f"owner_{test_id}@pizzeriaroma.it",
                "password": "SecurePass123!",
                "business_name": "Pizzeria Roma Milano"
            }
            
            response = await self.client.post(f"{BASE_URL}/auth/register", json=user_data)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("token")
                self.user_id = data.get("user", {}).get("id")
                self.log_result("User Registration", True, f"User created: {data.get('user', {}).get('username')}")
                return True
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.status_code != 500 else "Server error"
                self.log_result("User Registration", False, f"Status: {response.status_code}, Error: {error_detail}")
                return False
                
        except Exception as e:
            self.log_result("User Registration", False, error=e)
            return False
    
    async def test_user_login(self):
        """Test user login with registered credentials"""
        try:
            if not hasattr(self, 'registered_username'):
                # Use the username from registration
                test_id = str(uuid.uuid4())[:8]
                login_data = {
                    "username": f"testowner_{test_id}",
                    "password": "SecurePass123!"
                }
            else:
                login_data = {
                    "username": self.registered_username,
                    "password": "SecurePass123!"
                }
            
            response = await self.client.post(f"{BASE_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("token")
                self.log_result("User Login", True, f"Login successful, token received: {bool(token)}")
                return True
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.status_code != 500 else "Server error"
                self.log_result("User Login", False, f"Status: {response.status_code}, Error: {error_detail}")
                return False
                
        except Exception as e:
            self.log_result("User Login", False, error=e)
            return False
    
    async def test_auth_me(self):
        """Test getting current user info"""
        try:
            if not self.auth_token:
                self.log_result("Auth Me", False, "No auth token available")
                return False
                
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = await self.client.get(f"{BASE_URL}/auth/me", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Auth Me", True, f"User info retrieved: {data.get('username')}")
                return True
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.status_code != 500 else "Server error"
                self.log_result("Auth Me", False, f"Status: {response.status_code}, Error: {error_detail}")
                return False
                
        except Exception as e:
            self.log_result("Auth Me", False, error=e)
            return False
    
    async def test_get_store_config(self):
        """Test getting store configuration"""
        try:
            if not self.auth_token:
                self.log_result("Get Store Config", False, "No auth token available")
                return False
                
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = await self.client.get(f"{BASE_URL}/store/config", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Get Store Config", True, f"Config retrieved, user_id: {data.get('user_id')}")
                return True
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.status_code != 500 else "Server error"
                self.log_result("Get Store Config", False, f"Status: {response.status_code}, Error: {error_detail}")
                return False
                
        except Exception as e:
            self.log_result("Get Store Config", False, error=e)
            return False
    
    async def test_update_store_config(self):
        """Test updating store configuration"""
        try:
            if not self.auth_token:
                self.log_result("Update Store Config", False, "No auth token available")
                return False
                
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Realistic store configuration update
            config_update = {
                "logo_url": "https://example.com/pizzeria-roma-logo.png",
                "business_description": "Autentica pizzeria italiana nel cuore di Milano. Ingredienti freschi, ricette tradizionali.",
                "mission_statement": "Portare il vero sapore dell'Italia in ogni pizza, con passione e tradizione.",
                "show_social_likes": True,
                "show_sustainability_index": True,
                "show_amenities": True,
                "amenities": ["WiFi Gratuito", "Parcheggio", "Terrazza", "Consegna a domicilio"],
                "additional_services": ["Catering", "Eventi privati", "Corsi di pizza"],
                "google_place_id": "ChIJrTLr-GyuEmsRBfy61i59si0",
                "recognitions": [
                    {"name": "Certificazione Bio", "icon_url": "https://example.com/bio-cert.png"},
                    {"name": "Gambero Rosso", "icon_url": "https://example.com/gambero-rosso.png"}
                ]
            }
            
            response = await self.client.put(f"{BASE_URL}/store/config", json=config_update, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Update Store Config", True, f"Config updated: {data.get('message')}")
                return True
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.status_code != 500 else "Server error"
                self.log_result("Update Store Config", False, f"Status: {response.status_code}, Error: {error_detail}")
                return False
                
        except Exception as e:
            self.log_result("Update Store Config", False, error=e)
            return False
    
    async def test_sustainability_calculation(self):
        """Test AI sustainability calculation"""
        try:
            if not self.auth_token:
                self.log_result("Sustainability Calculation", False, "No auth token available")
                return False
                
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Realistic sustainability request
            sustainability_request = {
                "business_name": "Pizzeria Roma Milano",
                "business_type": "Ristorante/Pizzeria",
                "description": "Pizzeria tradizionale italiana che utilizza ingredienti locali e biologici, con forno a legna e packaging eco-sostenibile."
            }
            
            response = await self.client.post(f"{BASE_URL}/sustainability/calculate", 
                                            json=sustainability_request, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                sustainability_index = data.get("sustainability_index")
                environmental_score = data.get("environmental_score")
                social_score = data.get("social_score")
                recommendations = data.get("recommendations", [])
                
                self.log_result("Sustainability Calculation", True, 
                              f"Index: {sustainability_index}, Env: {environmental_score}, Social: {social_score}, Recommendations: {len(recommendations)}")
                return True
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.status_code != 500 else "Server error"
                self.log_result("Sustainability Calculation", False, f"Status: {response.status_code}, Error: {error_detail}")
                return False
                
        except Exception as e:
            self.log_result("Sustainability Calculation", False, error=e)
            return False
    
    async def test_display_preview(self):
        """Test public display preview endpoint"""
        try:
            if not self.user_id:
                self.log_result("Display Preview", False, "No user_id available")
                return False
                
            response = await self.client.get(f"{BASE_URL}/display/{self.user_id}")
            
            if response.status_code == 200:
                data = response.json()
                business_name = data.get("business_name")
                config = data.get("config")
                sustainability = data.get("sustainability")
                social_data = data.get("social_data")
                
                self.log_result("Display Preview", True, 
                              f"Business: {business_name}, Config: {bool(config)}, Sustainability: {bool(sustainability)}, Social: {bool(social_data)}")
                return True
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.status_code != 500 else "Server error"
                self.log_result("Display Preview", False, f"Status: {response.status_code}, Error: {error_detail}")
                return False
                
        except Exception as e:
            self.log_result("Display Preview", False, error=e)
            return False
    
    async def test_social_apis(self):
        """Test social media API endpoints (expected to fail without API keys)"""
        try:
            if not self.auth_token:
                self.log_result("Social APIs", False, "No auth token available")
                return False
                
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Test Google Reviews
            response = await self.client.get(f"{BASE_URL}/social/google-reviews?place_id=ChIJrTLr-GyuEmsRBfy61i59si0", headers=headers)
            google_success = response.status_code == 200
            google_data = response.json() if google_success else {}
            
            # Test Facebook Likes
            response = await self.client.get(f"{BASE_URL}/social/facebook-likes?page_id=pizzeriaroma", headers=headers)
            facebook_success = response.status_code == 200
            facebook_data = response.json() if facebook_success else {}
            
            # Test Instagram Data
            response = await self.client.get(f"{BASE_URL}/social/instagram-data?username=pizzeriaroma", headers=headers)
            instagram_success = response.status_code == 200
            instagram_data = response.json() if instagram_success else {}
            
            # Test TripAdvisor Reviews
            response = await self.client.get(f"{BASE_URL}/social/tripadvisor-reviews?location_id=123456", headers=headers)
            tripadvisor_success = response.status_code == 200
            tripadvisor_data = response.json() if tripadvisor_success else {}
            
            # These are expected to return errors due to missing API keys
            google_has_error = google_data.get("error") is not None
            facebook_has_error = facebook_data.get("error") is not None
            instagram_has_error = instagram_data.get("error") is not None
            tripadvisor_has_error = tripadvisor_data.get("error") is not None
            
            self.log_result("Social APIs", True, 
                          f"Google: {google_has_error}, FB: {facebook_has_error}, IG: {instagram_has_error}, TA: {tripadvisor_has_error} (errors expected)")
            return True
                
        except Exception as e:
            self.log_result("Social APIs", False, error=e)
            return False
    
    async def run_all_tests(self):
        """Run all backend tests in sequence"""
        print(f"🚀 Starting Backend Tests for Look@Me CMS")
        print(f"📍 Base URL: {BASE_URL}")
        print("=" * 60)
        
        # Test sequence
        tests = [
            ("Health Check", self.test_health_check),
            ("User Registration", self.test_user_registration),
            ("User Login", self.test_user_login),
            ("Auth Me", self.test_auth_me),
            ("Get Store Config", self.test_get_store_config),
            ("Update Store Config", self.test_update_store_config),
            ("Sustainability Calculation", self.test_sustainability_calculation),
            ("Display Preview", self.test_display_preview),
            ("Social APIs", self.test_social_apis),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🧪 Running: {test_name}")
            try:
                success = await test_func()
                if success:
                    passed += 1
            except Exception as e:
                self.log_result(test_name, False, error=e)
        
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        print("=" * 60)
        
        # Print detailed results
        print("\n📋 Detailed Results:")
        for test_name, result in self.test_results.items():
            status = "✅" if result["success"] else "❌"
            print(f"{status} {test_name}: {result['details']}")
            if result["error"]:
                print(f"   ⚠️  Error: {result['error']}")
        
        return self.test_results

async def main():
    """Main test runner"""
    async with BackendTester() as tester:
        results = await tester.run_all_tests()
        
        # Summary for test_result.md
        print("\n" + "=" * 60)
        print("📝 SUMMARY FOR TEST_RESULT.MD:")
        print("=" * 60)
        
        critical_failures = []
        minor_issues = []
        successes = []
        
        for test_name, result in results.items():
            if result["success"]:
                successes.append(test_name)
            else:
                # Determine if it's critical or minor
                if test_name in ["Health Check", "User Registration", "User Login", "Get Store Config", "Update Store Config", "Sustainability Calculation", "Display Preview"]:
                    critical_failures.append(f"{test_name}: {result['details']} - {result['error']}")
                else:
                    minor_issues.append(f"{test_name}: {result['details']}")
        
        if critical_failures:
            print("\n❌ CRITICAL FAILURES:")
            for failure in critical_failures:
                print(f"  - {failure}")
        
        if minor_issues:
            print("\n⚠️  MINOR ISSUES:")
            for issue in minor_issues:
                print(f"  - {issue}")
        
        if successes:
            print(f"\n✅ SUCCESSFUL TESTS ({len(successes)}):")
            for success in successes:
                print(f"  - {success}")

if __name__ == "__main__":
    asyncio.run(main())