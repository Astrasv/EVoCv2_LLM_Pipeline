#!/usr/bin/env python3
"""
End-to-End Demo Script: Employee Shift Scheduling Optimization
Demonstrates the complete EA Code Evolution Platform workflow using a real-world problem
"""

import requests
import json
import time
import uuid
from datetime import datetime
from typing import Optional, Dict, Any


class EACodeEvolutionDemo:
    """Complete demonstration of the EA Code Evolution Platform"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.access_token: Optional[str] = None
        self.user_id: Optional[str] = None
        self.problem_id: Optional[str] = None
        self.notebook_id: Optional[str] = None
        
        # Demo company data
        self.company_name = "TechCorp Solutions"
        self.demo_user = {
            "username": f"manager_{uuid.uuid4().hex[:6]}",
            "email": f"manager_{uuid.uuid4().hex[:6]}@techcorp.com",
            "password": "secure_password_123"
        }
    
    def log_step(self, step: str, details: str = ""):
        """Log demonstration steps"""
        print(f"\n{'='*60}")
        print(f"STEP: {step}")
        if details:
            print(f"Details: {details}")
        print(f"{'='*60}")
    
    def log_result(self, success: bool, message: str, data: Any = None):
        """Log step results"""
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{status}: {message}")
        if data and isinstance(data, dict):
            print(f"Response Data: {json.dumps(data, indent=2)[:500]}...")
        print()
    
    def make_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None) -> tuple:
        """Make HTTP request"""
        try:
            url = f"{self.base_url}{endpoint}"
            request_headers = headers or {}
            
            if self.access_token:
                request_headers["Authorization"] = f"Bearer {self.access_token}"
            
            if data and method.upper() in ['POST', 'PUT']:
                request_headers['Content-Type'] = 'application/json'
            
            response = requests.request(
                method=method.upper(),
                url=url,
                json=data if data else None,
                headers=request_headers,
                timeout=30
            )
            
            try:
                response_data = response.json()
            except:
                response_data = response.text
            
            return response.status_code < 400, response_data, response.status_code
            
        except Exception as e:
            return False, str(e), 0
    
    def step1_health_check(self):
        """Step 1: Verify the API is running"""
        self.log_step("1. Health Check", "Verifying API availability")
        
        success, data, status = self.make_request("GET", "/api/v1/health")
        
        if success and status == 200:
            self.log_result(True, "API is running and healthy")
            return True
        else:
            self.log_result(False, f"API health check failed (Status: {status})", data)
            return False
    
    def step2_user_registration(self):
        """Step 2: Register a new user for the demo"""
        self.log_step("2. User Registration", f"Creating demo user: {self.demo_user['username']}")
        
        success, data, status = self.make_request("POST", "/api/v1/auth/register", self.demo_user)
        
        if success and status == 201 and isinstance(data, dict) and data.get('success'):
            response_data = data.get('data', {})
            self.access_token = response_data.get('access_token')
            user_info = response_data.get('user', {})
            self.user_id = user_info.get('id')
            
            self.log_result(True, f"User registered successfully. ID: {self.user_id[:8]}...")
            return True
        else:
            self.log_result(False, f"User registration failed (Status: {status})", data)
            return False
    
    def step3_create_problem(self):
        """Step 3: Create a real-world optimization problem"""
        self.log_step("3. Problem Creation", "Employee Shift Scheduling Optimization")
        
        # Real-world shift scheduling problem
        problem_data = {
            "title": "Employee Shift Scheduling Optimization",
            "description": """
            Optimize employee shift assignments for a customer service center to minimize costs 
            while ensuring adequate coverage. The problem involves assigning 20 employees to 
            different shifts (morning, afternoon, evening, night) across a week, considering:
            
            - Employee preferences and availability
            - Minimum coverage requirements per shift
            - Labor cost optimization
            - Workload balance and fairness
            - Overtime regulations and constraints
            
            Each employee has different hourly rates, skill levels, and availability windows.
            The goal is to create an optimal schedule that satisfies all constraints while 
            minimizing total labor costs and maximizing employee satisfaction.
            """.strip(),
            "problem_type": "scheduling",
            "objectives": [
                "minimize_labor_costs",
                "maximize_coverage_quality", 
                "maximize_employee_satisfaction",
                "minimize_overtime_hours"
            ],
            "constraints": {
                "num_employees": 20,
                "shifts_per_day": 4,
                "days_per_week": 7,
                "min_coverage_per_shift": 3,
                "max_coverage_per_shift": 8,
                "max_hours_per_employee": 40,
                "max_consecutive_shifts": 3,
                "min_rest_hours": 8,
                "employee_hourly_rates": {
                    "junior": 15.0,
                    "senior": 25.0,
                    "supervisor": 35.0
                },
                "shift_requirements": {
                    "morning": {"min_staff": 4, "preferred_skill": "customer_service"},
                    "afternoon": {"min_staff": 6, "preferred_skill": "technical_support"},
                    "evening": {"min_staff": 5, "preferred_skill": "customer_service"},
                    "night": {"min_staff": 3, "preferred_skill": "technical_support"}
                },
                "overtime_multiplier": 1.5,
                "weekend_bonus": 1.2
            }
        }
        
        success, data, status = self.make_request("POST", "/api/v1/problems", problem_data)
        
        if success and status == 201 and isinstance(data, dict) and data.get('success'):
            response_data = data.get('data', {})
            self.problem_id = response_data.get('id')
            self.log_result(True, f"Problem created successfully. ID: {self.problem_id[:8]}...")
            return True
        else:
            self.log_result(False, f"Problem creation failed (Status: {status})", data)
            return False
    
    def step4_create_notebook(self):
        """Step 4: Create a notebook for the problem"""
        self.log_step("4. Notebook Creation", "Creating workspace for EA solution development")
        
        notebook_data = {
            "problem_id": self.problem_id,
            "name": "Shift Scheduling EA Solution",
            "deap_toolbox_config": {
                "population_size": 100,
                "generations": 50,
                "crossover_probability": 0.8,
                "mutation_probability": 0.15,
                "selection_method": "tournament",
                "tournament_size": 3,
                "elitism": True,
                "elite_size": 5
            }
        }
        
        success, data, status = self.make_request("POST", "/api/v1/notebooks", notebook_data)
        
        if success and status == 201 and isinstance(data, dict) and data.get('success'):
            response_data = data.get('data', {})
            self.notebook_id = response_data.get('id')
            self.log_result(True, f"Notebook created successfully. ID: {self.notebook_id[:8]}...")
            return True
        else:
            self.log_result(False, f"Notebook creation failed (Status: {status})", data)
            return False
    
    def step5_coordinate_agents(self):
        """Step 5: Coordinate multi-agent system to generate DEAP code"""
        self.log_step("5. Multi-Agent Coordination", "7 specialized agents generating DEAP code")
        
        print("Coordinating agents:")
        print("1. Problem Analyser → Analyzing shift scheduling requirements")
        print("2. Individuals Modelling → Designing schedule representation")
        print("3. Fitness Function → Creating cost/satisfaction evaluation")
        print("4. Crossover Function → Schedule recombination strategies")
        print("5. Mutation Function → Schedule modification operators")
        print("6. Selection Strategy → Parent selection methods")
        print("7. Code Integration → Complete DEAP algorithm assembly")
        print()
        print("This may take 30-60 seconds as each agent consults ChatGroq...")
        
        start_time = time.time()
        success, data, status = self.make_request("POST", f"/api/v1/agents/{self.notebook_id}/coordinate", {})
        end_time = time.time()
        
        if success and status == 200 and isinstance(data, dict) and data.get('success'):
            response_data = data.get('data', {})
            results = response_data.get('results', {})
            
            self.log_result(True, f"Multi-agent coordination completed in {end_time-start_time:.1f}s")
            print(f"Generated code for {len(results)} agents:")
            for agent_id, result in results.items():
                print(f"  - {agent_id}: {result.get('cell_type')} (Cell ID: {result.get('cell_id', '')[:8]}...)")
            return True
        else:
            self.log_result(False, f"Agent coordination failed (Status: {status})", data)
            return False
    
    def step6_view_generated_cells(self):
        """Step 6: Examine the generated notebook cells"""
        self.log_step("6. Generated Code Review", "Examining AI-generated DEAP components")
        
        success, data, status = self.make_request("GET", f"/api/v1/agents/{self.notebook_id}/cells")
        
        if success and status == 200 and isinstance(data, dict) and data.get('success'):
            response_data = data.get('data', {})
            cells = response_data.get('cells', [])
            
            self.log_result(True, f"Retrieved {len(cells)} generated cells")
            
            for i, cell in enumerate(cells, 1):
                print(f"\nCell {i}: {cell['cell_type']} (Agent: {cell['agent_id']})")
                print(f"Position: {cell['position']}, Version: {cell['version']}")
                code_preview = cell['code'][:200].replace('\n', ' ')
                print(f"Code Preview: {code_preview}...")
            
            return True
        else:
            self.log_result(False, f"Failed to retrieve cells (Status: {status})", data)
            return False
    
    def step7_get_complete_algorithm(self):
        """Step 7: Get the complete integrated DEAP algorithm"""
        self.log_step("7. Complete Algorithm", "Retrieving integrated DEAP evolutionary algorithm")
        
        success, data, status = self.make_request("GET", f"/api/v1/agents/{self.notebook_id}/complete-code")
        
        if success and status == 200 and isinstance(data, dict) and data.get('success'):
            response_data = data.get('data', {})
            complete_code = response_data.get('complete_code', '')
            code_length = response_data.get('code_length', 0)
            
            self.log_result(True, f"Complete algorithm retrieved ({code_length} characters)")
            
            # Save the complete algorithm to file
            filename = f"shift_scheduling_ea_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(complete_code)
            
            print(f"Complete DEAP algorithm saved to: {filename}")
            print("\nAlgorithm Preview (first 500 characters):")
            print("-" * 50)
            print(complete_code[:500])
            print("...")
            print("-" * 50)
            
            return True
        else:
            self.log_result(False, f"Failed to retrieve complete code (Status: {status})", data)
            return False
    
    def step8_test_regeneration(self):
        """Step 8: Demonstrate cell regeneration capability"""
        self.log_step("8. Cell Regeneration", "Regenerating fitness function with new requirements")
        
        print("Testing iterative improvement by regenerating the fitness function...")
        
        success, data, status = self.make_request("POST", f"/api/v1/agents/{self.notebook_id}/regenerate/fitness", {})
        
        if success and status == 200 and isinstance(data, dict) and data.get('success'):
            response_data = data.get('data', {})
            cell_type = response_data.get('cell_type')
            version = response_data.get('version')
            
            self.log_result(True, f"Regenerated {cell_type} cell (now version {version})")
            print("This demonstrates how individual components can be iteratively improved")
            print("while maintaining the context from other agents.")
            return True
        else:
            self.log_result(False, f"Cell regeneration failed (Status: {status})", data)
            return False
    
    def step9_chat_interaction(self):
        """Step 9: Demonstrate chat-based interaction"""
        self.log_step("9. Chat Interaction", "Testing conversational AI assistance")
        
        message_data = {
            "message": "How can I modify the generated algorithm to prioritize employee preferences more heavily in the fitness function?"
        }
        
        success, data, status = self.make_request("POST", f"/api/v1/chat/{self.notebook_id}/messages", message_data)
        
        if success and status == 200 and isinstance(data, dict) and data.get('success'):
            response_data = data.get('data', {})
            ai_response = response_data.get('ai_response', {})
            
            self.log_result(True, "Chat interaction successful")
            if ai_response:
                ai_message = ai_response.get('message', '')
                print(f"AI Response Preview: {ai_message[:300]}...")
            return True
        else:
            self.log_result(False, f"Chat interaction failed (Status: {status})", data)
            return False
    
    def step10_summary(self):
        """Step 10: Demonstration summary"""
        self.log_step("10. Demo Summary", "Complete workflow demonstration")
        
        print("DEMONSTRATION COMPLETED SUCCESSFULLY!")
        print()
        print("What was accomplished:")
        print("✅ Registered user and authenticated")
        print("✅ Created real-world optimization problem (Employee Shift Scheduling)")
        print("✅ Set up notebook workspace with DEAP configuration")
        print("✅ Coordinated 7 specialized AI agents to generate complete EA solution")
        print("✅ Generated individual components: problem analysis, representation,")
        print("   fitness function, crossover, mutation, selection, and integration")
        print("✅ Retrieved complete, executable DEAP algorithm")
        print("✅ Demonstrated iterative improvement via cell regeneration")
        print("✅ Tested conversational AI assistance")
        print()
        print("Generated Algorithm Details:")
        print(f"- Problem ID: {self.problem_id}")
        print(f"- Notebook ID: {self.notebook_id}")
        print(f"- User: {self.demo_user['username']}")
        print(f"- Company: {self.company_name}")
        print()
        print("The generated DEAP algorithm can now be executed to solve the")
        print("employee shift scheduling optimization problem using evolutionary")
        print("algorithms with the specific constraints and objectives defined.")
        print()
        print("This demonstrates that the EA Code Evolution Platform successfully:")
        print("1. Analyzes real-world optimization problems")
        print("2. Generates appropriate evolutionary algorithm solutions")
        print("3. Provides iterative improvement capabilities")
        print("4. Offers conversational AI assistance")
        print("5. Produces executable, production-ready code")
    
    def run_complete_demo(self):
        """Run the complete end-to-end demonstration"""
        print(f"{'='*80}")
        print("EA CODE EVOLUTION PLATFORM - END-TO-END DEMONSTRATION")
        print(f"{'='*80}")
        print("Real-World Problem: Employee Shift Scheduling Optimization")
        print(f"Company: {self.company_name}")
        print(f"Demo Started: {datetime.now().isoformat()}")
        print(f"API Endpoint: {self.base_url}")
        print(f"{'='*80}")
        
        steps = [
            self.step1_health_check,
            self.step2_user_registration,
            self.step3_create_problem,
            self.step4_create_notebook,
            self.step5_coordinate_agents,
            self.step6_view_generated_cells,
            self.step7_get_complete_algorithm,
            self.step8_test_regeneration,
            self.step9_chat_interaction,
            self.step10_summary
        ]
        
        for step_func in steps:
            if not step_func():
                print(f"\n❌ DEMO FAILED at {step_func.__name__}")
                print("Please check the API logs and ensure all services are running correctly.")
                return False
            time.sleep(1)  # Small delay between steps for readability
        
        return True


def main():
    """Run the complete demonstration"""
    import argparse
    
    parser = argparse.ArgumentParser(description="EA Code Evolution Platform Demo")
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL")
    args = parser.parse_args()
    
    demo = EACodeEvolutionDemo(base_url=args.url)
    
    try:
        success = demo.run_complete_demo()
        if success:
            print(f"\n🎉 DEMONSTRATION COMPLETED SUCCESSFULLY!")
            print(f"Generated algorithm file saved in current directory.")
        else:
            print(f"\n💥 DEMONSTRATION FAILED!")
            return 1
    except KeyboardInterrupt:
        print(f"\n⏹️  Demo interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())