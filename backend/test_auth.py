#!/usr/bin/env python3
"""
Quick test script for authentication endpoints
"""
import requests
import json

API_BASE = "http://localhost:8000"

def test_signup():
    """Test user registration"""
    url = f"{API_BASE}/auth/register"
    payload = {
        "email": "testuser4@example.com",
        "password": "TestPass123",
        "software_background": "Intermediate",
        "hardware_background": "Basic",
        "python_familiar": True,
        "ros_familiar": False,
        "aiml_familiar": True
    }

    print(f"Testing POST {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(url, json=payload)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")

        try:
            print(f"Response JSON: {json.dumps(response.json(), indent=2)}")
        except:
            print(f"Response Text: {response.text}")

        return response
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_login():
    """Test user login"""
    url = f"{API_BASE}/auth/login"
    data = {
        "username": "testuser4@example.com",
        "password": "TestPass123"
    }

    print(f"\n\nTesting POST {url}")
    print(f"Payload: {data}")

    try:
        response = requests.post(url, data=data)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")

        try:
            print(f"Response JSON: {json.dumps(response.json(), indent=2)}")
        except:
            print(f"Response Text: {response.text}")

        return response
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("SIGNUP TEST")
    print("=" * 60)
    signup_response = test_signup()

    if signup_response and signup_response.status_code == 201:
        print("\n" + "=" * 60)
        print("LOGIN TEST")
        print("=" * 60)
        login_response = test_login()
