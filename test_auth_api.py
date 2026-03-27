import requests
import uuid

API_URL = "http://localhost:8000/api/auth"

def test_auth():
    # 1. Register
    test_email = f"test_{uuid.uuid4().hex[:6]}@example.com"
    test_password = "password123"
    
    reg_payload = {
        "name": "Test User",
        "email": test_email,
        "password": test_password
    }
    
    print(f"[*] Registering {test_email}...")
    res = requests.post(f"{API_URL}/register", json=reg_payload)
    print(f"Register status: {res.status_code}")
    print(f"Register response: {res.json()}")
    
    assert res.status_code == 201, "Registration failed"
    
    # 2. Login
    login_payload = {
        "email": test_email,
        "password": test_password
    }
    print(f"\n[*] Logging in as {test_email}...")
    res = requests.post(f"{API_URL}/login", json=login_payload)
    print(f"Login status: {res.status_code}")
    print(f"Login response: {res.json()}")
    
    assert res.status_code == 200, "Login failed"
    assert "access_token" in res.json(), "No access token in response"
    print("\n[+] Auth system is working perfectly!")

if __name__ == "__main__":
    test_auth()
