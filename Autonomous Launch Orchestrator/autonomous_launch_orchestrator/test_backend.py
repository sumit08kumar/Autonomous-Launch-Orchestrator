#!/usr/bin/env python3
"""
Test script for the Autonomous Launch Orchestrator backend
"""

import sys
import os
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.core.agents import PlannerAgent, RoleAgent
from backend.app.core.n8n_integration import N8NIntegration

def test_planner_agent():
    """Test the PlannerAgent functionality"""
    print("Testing PlannerAgent...")
    
    planner = PlannerAgent()
    goal = "Launch our new AI chatbot in 3 weeks"
    
    try:
        tasks = planner.create_launch_plan(goal)
        print(f"✅ PlannerAgent created {len(tasks)} tasks")
        
        for task in tasks[:2]:  # Show first 2 tasks
            print(f'  - {task["role"]}: {task["description"][:50]}...')
        
        return True
    except Exception as e:
        print(f"❌ PlannerAgent failed: {e}")
        return False

def test_role_agent():
    """Test the RoleAgent functionality"""
    print("\nTesting RoleAgent...")
    
    try:
        marketing_agent = RoleAgent("marketing")
        content = marketing_agent.generate_content("Create social media campaign for AI chatbot launch")
        
        print(f"✅ RoleAgent generated content ({len(content)} characters)")
        print(f"  Sample: {content[:100]}...")
        
        return True
    except Exception as e:
        print(f"❌ RoleAgent failed: {e}")
        return False

def test_n8n_integration():
    """Test the N8NIntegration functionality"""
    print("\nTesting N8NIntegration...")
    
    try:
        base = os.getenv("N8N_BASE_URL", "http://localhost:5678")
        n8n = N8NIntegration(base)

        # Test workflow mapping (no assertion on value)
        workflow = n8n.map_task_to_workflow("marketing", "social_media")
        print(f"✅ N8NIntegration mapped workflow: {workflow}")

        # Prefer an env-provided webhook for a real 200 from n8n Cloud
        wf_to_call = os.getenv("N8N_WEBHOOK_TEST_WORKFLOW", "marketing_general")
        result = n8n.trigger_workflow(wf_to_call, {"test": "data"})
        print(f"✅ N8NIntegration trigger test completed (status: {result['status']})")
        
        return True
    except Exception as e:
        print(f"❌ N8NIntegration failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Autonomous Launch Orchestrator Backend Components\n")
    
    tests = [
        test_planner_agent,
        test_role_agent,
        test_n8n_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())

