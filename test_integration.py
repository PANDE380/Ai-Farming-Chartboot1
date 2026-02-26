#!/usr/bin/env python3
"""Simple test to verify frontend-backend connections."""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_endpoints():
    print("=" * 60)
    print("AI Farming Chatbot - Frontend/Backend Integration Tests")
    print("=" * 60)
    
    # Test 1: Check if server is running
    print("\n[1] Testing server connection...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✓ Server is running")
        else:
            print(f"✗ Server returned status {response.status_code}")
    except Exception as e:
        print(f"✗ Cannot connect to server: {e}")
        print("  Make sure server is running: python run.py")
        return
    
    # Test 2: Test user signup
    print("\n[2] Testing user signup endpoint...")
    try:
        response = requests.post(
            f"{BASE_URL}/signup",
            json={
                "username": f"testuser_{int(time.time())}",
                "email": f"test_{int(time.time())}@test.com",
                "password": "testpass123"
            }
        )
        if response.status_code == 200:
            print("✓ Signup endpoint working")
        else:
            print(f"✗ Signup failed: {response.json()}")
    except Exception as e:
        print(f"✗ Signup test error: {e}")
    
    # Test 3: Test user login
    print("\n[3] Testing user login endpoint...")
    try:
        response = requests.post(
            f"{BASE_URL}/user/login",
            json={
                "username": "demo",
                "password": "demo123"
            }
        )
        if response.status_code == 200:
            data = response.json()
            token = data.get("token")
            print(f"✓ User login working (token: {token[:10]}...)")
            
            # Test 4: Test chat endpoint with token
            print("\n[4] Testing chat endpoint...")
            try:
                response = requests.post(
                    f"{BASE_URL}/chat",
                    json={"message": "What are common crop diseases?"},
                    headers={"x-token": token}
                )
                if response.status_code == 200:
                    data = response.json()
                    reply = data.get("reply", "")
                    print(f"✓ Chat endpoint working")
                    print(f"  Bot response: {reply[:80]}...")
                else:
                    print(f"✗ Chat failed: {response.json()}")
            except Exception as e:
                print(f"✗ Chat test error: {e}")
        else:
            print(f"✗ Login failed: {response.json()}")
    except Exception as e:
        print(f"✗ Login test error: {e}")
    
    # Test 5: Test public chat (no token)
    print("\n[5] Testing public chat endpoint...")
    try:
        response = requests.get(
            f"{BASE_URL}/chat?message=What%20is%20irrigation?"
        )
        if response.status_code == 200:
            data = response.json()
            reply = data.get("reply", "")
            print(f"✓ Public chat working")
            print(f"  Bot response: {reply[:80]}...")
        else:
            print(f"✗ Public chat failed")
    except Exception as e:
        print(f"✗ Public chat test error: {e}")
    
    # Test 6: Test admin login
    print("\n[6] Testing admin login endpoint...")
    try:
        response = requests.post(
            f"{BASE_URL}/admin/login",
            json={
                "username": "admin",
                "password": "admin123"
            }
        )
        if response.status_code == 200:
            data = response.json()
            admin_token = data.get("token")
            print(f"✓ Admin login working (token: {admin_token[:10]}...)")
            
            # Test 7: Test knowledge base endpoint
            print("\n[7] Testing knowledge base endpoint...")
            try:
                response = requests.get(
                    f"{BASE_URL}/admin/knowledge",
                    headers={"x-token": admin_token}
                )
                if response.status_code == 200:
                    data = response.json()
                    count = len(data)
                    print(f"✓ Knowledge base endpoint working ({count} entries)")
                else:
                    print(f"✗ Knowledge base fetch failed")
            except Exception as e:
                print(f"✗ Knowledge base test error: {e}")
        else:
            print(f"✗ Admin login failed: {response.json()}")
    except Exception as e:
        print(f"✗ Admin login test error: {e}")
    
    print("\n" + "=" * 60)
    print("Frontend URLs Available:")
    print("=" * 60)
    print(f"Home: {BASE_URL}/")
    print(f"Signup: {BASE_URL}/signup")
    print(f"Login: {BASE_URL}/login")
    print(f"Chat: {BASE_URL}/chat")
    print(f"Admin: {BASE_URL}/admin")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_endpoints()
