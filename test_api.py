

import asyncio
import aiohttp
import json
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
import sys


class APITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Store IDs for dependent tests
        self.access_token: Optional[str] = None
        self.user_id: Optional[str] = None
        self.problem_id: Optional[str] = None
        self.notebook_id: Optional[str] = None
        self.session_id: Optional[str] = None
        
        # Test results
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_result(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            self.failed_tests += 1
            status = "❌ FAIL"
        
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "response_data": response_data
        }
        self.results.append(result)
        print(f"{status} | {test_name}")
        if details:
            print(f"      {details}")
        if not success and response_data:
            print(f"      Response: {response_data}")
        print()
    
    async def make_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None) -> tuple:
        """Make HTTP request and return (success, response_data, status_code)"""
        try:
            url = f"{self.base_url}{endpoint}"
            request_headers = headers or {}
            
            if data and method.upper() in ['POST', 'PUT']:
                request_headers['Content-Type'] = 'application/json'
            
            async with self.session.request(
                method=method.upper(),
                url=url,
                json=data if data else None,
                headers=request_headers
            ) as response:
                try:
                    response_data = await response.json()
                except:
                    response_data = await response.text()
                
                return response.status < 400, response_data, response.status
                
        except Exception as e:
            return False, str(e), 0
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authorization headers"""
        if not self.access_token:
            return {}
        return {"Authorization": f"Bearer {self.access_token}"}
    
    # Health Check Tests
    async def test_health_basic(self):
        """Test basic health check"""
        success, data, status = await self.make_request("GET", "/api/v1/health")
        self.log_result(
            "Health Check - Basic",
            success and status == 200,
            f"Status: {status}",
            data if not success else None
        )
    
    async def test_health_detailed(self):
        """Test detailed health check"""
        success, data, status = await self.make_request("GET", "/api/v1/health/detailed")
        self.log_result(
            "Health Check - Detailed",
            success and status in [200, 503],  # 503 is acceptable if some services are down
            f"Status: {status}",
            data if not success else None
        )
    
    # Authentication Tests
    async def test_user_registration(self):
        """Test user registration"""
        test_user = {
            "username": f"testuser_{uuid.uuid4().hex[:8]}",
            "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
            "password": "testpassword123"
        }
        
        success, data, status = await self.make_request("POST", "/api/v1/auth/register", test_user)
        
        if success and status == 201 and isinstance(data, dict) and data.get('success'):
            # Store access token for subsequent tests
            response_data = data.get('data', {})
            self.access_token = response_data.get('access_token')
            user_info = response_data.get('user', {})
            self.user_id = user_info.get('id')
            
            self.log_result(
                "User Registration", 
                True, 
                f"User ID: {self.user_id[:8] if self.user_id else 'None'}..."
            )
        else:
            self.log_result(
                "User Registration", 
                False, 
                f"Status: {status}", 
                data
            )
    
    async def test_user_login(self):
        """Test user login (if registration failed)"""
        if self.access_token:
            self.log_result("User Login", True, "Skipped - already have token from registration")
            return
        
        # Try with a test user (this will likely fail, but good to test the endpoint)
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        success, data, status = await self.make_request("POST", "/api/v1/auth/login", login_data)
        
        if success and status == 200 and isinstance(data, dict) and data.get('success'):
            response_data = data.get('data', {})
            self.access_token = response_data.get('access_token')
            self.log_result("User Login", True, "Login successful")
        else:
            self.log_result("User Login", False, f"Status: {status} (Expected if test user doesn't exist)", data)
    
    # User Management Tests
    async def test_get_current_user(self):
        """Test get current user"""
        if not self.access_token:
            self.log_result("Get Current User", False, "No access token available")
            return
        
        success, data, status = await self.make_request(
            "GET", "/api/v1/users/me", 
            headers=self.get_auth_headers()
        )
        
        self.log_result(
            "Get Current User",
            success and status == 200,
            f"Status: {status}",
            data if not success else None
        )
    
    async def test_update_current_user(self):
        """Test update current user"""
        if not self.access_token:
            self.log_result("Update Current User", False, "No access token available")
            return
        
        update_data = {"subscription_tier": "premium"}
        
        success, data, status = await self.make_request(
            "PUT", "/api/v1/users/me", 
            data=update_data,
            headers=self.get_auth_headers()
        )
        
        self.log_result(
            "Update Current User",
            success and status == 200,
            f"Status: {status}",
            data if not success else None
        )
    
    # Problem Management Tests
    async def test_create_problem(self):
        """Test create problem"""
        if not self.access_token:
            self.log_result("Create Problem", False, "No access token available")
            return
        
        problem_data = {
            "title": "Test Knapsack Problem",
            "description": "A test optimization problem for the API test suite",
            "problem_type": "optimization",
            "objectives": ["maximize_value", "minimize_weight"],
            "constraints": {
                "weight_limit": 100,
                "items": [
                    {"weight": 10, "value": 60},
                    {"weight": 20, "value": 100}
                ]
            }
        }
        
        success, data, status = await self.make_request(
            "POST", "/api/v1/problems",
            data=problem_data,
            headers=self.get_auth_headers()
        )
        
        if success and status == 201 and isinstance(data, dict) and data.get('success'):
            response_data = data.get('data', {})
            self.problem_id = response_data.get('id')
            self.log_result(
                "Create Problem", 
                True, 
                f"Problem ID: {self.problem_id[:8] if self.problem_id else 'None'}..."
            )
        else:
            self.log_result(
                "Create Problem", 
                False, 
                f"Status: {status}", 
                data
            )
    
    async def test_list_problems(self):
        """Test list problems"""
        if not self.access_token:
            self.log_result("List Problems", False, "No access token available")
            return
        
        success, data, status = await self.make_request(
            "GET", "/api/v1/problems?page=1&size=10",
            headers=self.get_auth_headers()
        )
        
        self.log_result(
            "List Problems",
            success and status == 200,
            f"Status: {status}",
            data if not success else None
        )
    
    async def test_get_problem(self):
        """Test get specific problem"""
        if not self.access_token or not self.problem_id:
            self.log_result("Get Problem", False, "No access token or problem ID available")
            return
        
        success, data, status = await self.make_request(
            "GET", f"/api/v1/problems/{self.problem_id}",
            headers=self.get_auth_headers()
        )
        
        self.log_result(
            "Get Problem",
            success and status == 200,
            f"Status: {status}",
            data if not success else None
        )
    
    async def test_update_problem(self):
        """Test update problem"""
        if not self.access_token or not self.problem_id:
            self.log_result("Update Problem", False, "No access token or problem ID available")
            return
        
        update_data = {
            "title": "Updated Test Knapsack Problem",
            "constraints": {"weight_limit": 150}
        }
        
        success, data, status = await self.make_request(
            "PUT", f"/api/v1/problems/{self.problem_id}",
            data=update_data,
            headers=self.get_auth_headers()
        )
        
        self.log_result(
            "Update Problem",
            success and status == 200,
            f"Status: {status}",
            data if not success else None
        )
    
    # Notebook Management Tests
    async def test_create_notebook(self):
        """Test create notebook"""
        if not self.access_token or not self.problem_id:
            self.log_result("Create Notebook", False, "No access token or problem ID available")
            return
        
        notebook_data = {
            "problem_id": self.problem_id,
            "name": "Test EA Solution Notebook",
            "deap_toolbox_config": {
                "population_size": 100,
                "generations": 50
            }
        }
        
        success, data, status = await self.make_request(
            "POST", "/api/v1/notebooks",
            data=notebook_data,
            headers=self.get_auth_headers()
        )
        
        if success and status == 201 and isinstance(data, dict) and data.get('success'):
            response_data = data.get('data', {})
            self.notebook_id = response_data.get('id')
            self.log_result(
                "Create Notebook", 
                True, 
                f"Notebook ID: {self.notebook_id[:8] if self.notebook_id else 'None'}..."
            )
        else:
            self.log_result(
                "Create Notebook", 
                False, 
                f"Status: {status}", 
                data
            )
    
    async def test_list_notebooks(self):
        """Test list notebooks"""
        if not self.access_token:
            self.log_result("List Notebooks", False, "No access token available")
            return
        
        success, data, status = await self.make_request(
            "GET", "/api/v1/notebooks?page=1&size=10",
            headers=self.get_auth_headers()
        )
        
        self.log_result(
            "List Notebooks",
            success and status == 200,
            f"Status: {status}",
            data if not success else None
        )
    
    async def test_get_notebook(self):
        """Test get specific notebook"""
        if not self.access_token or not self.notebook_id:
            self.log_result("Get Notebook", False, "No access token or notebook ID available")
            return
        
        success, data, status = await self.make_request(
            "GET", f"/api/v1/notebooks/{self.notebook_id}",
            headers=self.get_auth_headers()
        )
        
        self.log_result(
            "Get Notebook",
            success and status == 200,
            f"Status: {status}",
            data if not success else None
        )
    
    # ChatGroq Integration Tests
    async def test_chatgroq_connection(self):
        """Test ChatGroq connection"""
        success, data, status = await self.make_request("GET", "/api/v1/chat/test-groq")
        
        self.log_result(
            "ChatGroq Connection Test",
            success and status == 200,
            f"Status: {status}",
            data if not success else None
        )
    
    async def test_send_chat_message(self):
        """Test send chat message"""
        if not self.access_token or not self.notebook_id:
            self.log_result("Send Chat Message", False, "No access token or notebook ID available")
            return
        
        message_data = {
            "message": "Hello! Can you help me with evolutionary algorithms?"
        }
        
        success, data, status = await self.make_request(
            "POST", f"/api/v1/chat/{self.notebook_id}/messages",
            data=message_data,
            headers=self.get_auth_headers()
        )
        
        self.log_result(
            "Send Chat Message",
            success and status == 200,
            f"Status: {status}",
            data if not success else None
        )
    
    async def test_generate_code(self):
        """Test code generation"""
        if not self.access_token or not self.notebook_id:
            self.log_result("Generate Code", False, "No access token or notebook ID available")
            return
        
        code_request = {
            "code_type": "fitness",
            "feedback": "I need a fitness function that maximizes profit while minimizing cost"
        }
        
        success, data, status = await self.make_request(
            "POST", f"/api/v1/chat/{self.notebook_id}/generate-code",
            data=code_request,
            headers=self.get_auth_headers()
        )
        
        self.log_result(
            "Generate Code",
            success and status == 200,
            f"Status: {status}",
            data if not success else None
        )
    
    async def test_get_chat_history(self):
        """Test get chat history"""
        if not self.access_token or not self.notebook_id:
            self.log_result("Get Chat History", False, "No access token or notebook ID available")
            return
        
        success, data, status = await self.make_request(
            "GET", f"/api/v1/chat/{self.notebook_id}/history?page=1&size=10",
            headers=self.get_auth_headers()
        )
        
        self.log_result(
            "Get Chat History",
            success and status == 200,
            f"Status: {status}",
            data if not success else None
        )
    
    # Evolution Tests
    async def test_start_evolution(self):
        """Test start evolution"""
        if not self.access_token or not self.notebook_id:
            self.log_result("Start Evolution", False, "No access token or notebook ID available")
            return
        
        evolution_config = {
            "max_iterations": 5,
            "population_size": 50
        }
        
        success, data, status = await self.make_request(
            "POST", f"/api/v1/evolution/{self.notebook_id}/start",
            data=evolution_config,
            headers=self.get_auth_headers()
        )
        
        if success and status == 200 and isinstance(data, dict) and data.get('success'):
            response_data = data.get('data', {})
            self.session_id = response_data.get('session_id')
            self.log_result("Start Evolution", True, f"Session ID: {self.session_id[:8] if self.session_id else 'None'}...")
        else:
            self.log_result(
                "Start Evolution", 
                False, 
                f"Status: {status}", 
                data
            )
    
    async def test_evolution_status(self):
        """Test get evolution status"""
        if not self.access_token or not self.session_id:
            self.log_result("Evolution Status", False, "No access token or session ID available")
            return
        
        success, data, status = await self.make_request(
            "GET", f"/api/v1/evolution/{self.session_id}/status",
            headers=self.get_auth_headers()
        )
        
        self.log_result(
            "Evolution Status",
            success and status == 200,
            f"Status: {status}",
            data if not success else None
        )
    
    # Cleanup Tests (Optional)
    async def test_delete_problem(self):
        """Test delete problem (cleanup)"""
        if not self.access_token or not self.problem_id:
            self.log_result("Delete Problem (Cleanup)", True, "Skipped - no problem to delete")
            return
        
        success, data, status = await self.make_request(
            "DELETE", f"/api/v1/problems/{self.problem_id}",
            headers=self.get_auth_headers()
        )
        
        self.log_result(
            "Delete Problem (Cleanup)",
            success and status == 200,
            f"Status: {status}",
            data if not success else None
        )
    
    async def run_all_tests(self):
        """Run all API tests"""
        print("=" * 60)
        print("EA CODE EVOLUTION PLATFORM - API TEST SUITE")
        print("=" * 60)
        print(f"Testing API at: {self.base_url}")
        print(f"Started at: {datetime.now().isoformat()}")
        print("=" * 60)
        print()
        
        # Health Tests
        print("🏥 HEALTH CHECKS")
        print("-" * 40)
        await self.test_health_basic()
        await self.test_health_detailed()
        
        # Authentication Tests
        print("🔐 AUTHENTICATION")
        print("-" * 40)
        await self.test_user_registration()
        await self.test_user_login()
        await self.test_get_current_user()
        await self.test_update_current_user()
        
        # Problem Management Tests
        print("📋 PROBLEM MANAGEMENT")
        print("-" * 40)
        await self.test_create_problem()
        await self.test_list_problems()
        await self.test_get_problem()
        await self.test_update_problem()
        
        # Notebook Management Tests
        print("📓 NOTEBOOK MANAGEMENT")
        print("-" * 40)
        await self.test_create_notebook()
        await self.test_list_notebooks()
        await self.test_get_notebook()
        
        # ChatGroq Integration Tests
        print("🤖 CHATGROQ INTEGRATION")
        print("-" * 40)
        await self.test_chatgroq_connection()
        await self.test_send_chat_message()
        await self.test_generate_code()
        await self.test_get_chat_history()
        
        # Evolution Tests
        print("🧬 EVOLUTION ENGINE")
        print("-" * 40)
        await self.test_start_evolution()
        await self.test_evolution_status()
        
        # Cleanup Tests
        print("🧹 CLEANUP")
        print("-" * 40)
        await self.test_delete_problem()
        
        # Results Summary
        print("=" * 60)
        print("TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        print()
        
        if self.failed_tests > 0:
            print("FAILED TESTS:")
            print("-" * 40)
            for result in self.results:
                if not result['success']:
                    print(f"❌ {result['test']}")
                    if result['details']:
                        print(f"   {result['details']}")
            print()
        
        print(f"Completed at: {datetime.now().isoformat()}")
        print("=" * 60)
        
        return self.failed_tests == 0


async def main():
    """Run the API test suite"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test EA Code Evolution Platform API")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL of the API")
    args = parser.parse_args()
    
    async with APITester(base_url=args.url) as tester:
        success = await tester.run_all_tests()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())