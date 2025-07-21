import requests
import json

# Token from localStorage
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc1MjExNDE3NCwianRpIjoiNWY5ZjhiMTctMGY0YS00NDk3LWJjZDUtYjI1YzIzNTYyZjEyIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6Ijc3MGU4NDAwLWUyOWItNDFkNC1hNzE2LTQ0NjY1NTQ0MDAwMSIsIm5iZiI6MTc1MjExNDE3NCwicm9sZSI6InN1cGVyYWRtaW4iLCJjbGllbnRfaWQiOm51bGwsInNpdGVfaWRzIjpbXSwibmFtZSI6IkJlbmphbWluIEFoYXJvbm92IiwiZW1haWwiOiJiYUBsYW5ldC5teCJ9.OHjQeIMlmSQRCb-J0q3t8eq31Lmso40hMArZnfZZ740"

# Asset ID to test
asset_id = "aa0e8400-e29b-41d4-a716-446655440001"

# Headers
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Test basic test endpoint first
test_url = "http://localhost:5001/api/assets/test"
print(f"Testing basic test URL: {test_url}")

try:
    test_response = requests.get(test_url)
    print(f"Basic Test Status Code: {test_response.status_code}")
    print(f"Basic Test Response: {test_response.text}")
except Exception as e:
    print(f"Basic Test Error: {e}")

# Test simple app first
simple_app_url = "http://localhost:5002/api/assets/simple-test"
print(f"Testing simple app URL: {simple_app_url}")

try:
    simple_app_response = requests.get(simple_app_url)
    print(f"Simple App Status Code: {simple_app_response.status_code}")
    print(f"Simple App Response: {simple_app_response.text}")
except Exception as e:
    print(f"Simple App Error: {e}")

# Test debug routes endpoint
debug_routes_url = "http://localhost:5001/api/assets/debug-routes"
print(f"Testing debug routes URL: {debug_routes_url}")

try:
    debug_response = requests.get(debug_routes_url)
    print(f"Debug Routes Status Code: {debug_response.status_code}")
    if debug_response.status_code == 200:
        data = debug_response.json()
        print(f"Total routes: {data.get('total', 0)}")
        for route in data.get('routes', []):
            if 'assets' in route['endpoint']:
                print(f"  {route['endpoint']}: {route['rule']}")
    else:
        print(f"Debug Routes Response: {debug_response.text}")
except Exception as e:
    print(f"Debug Routes Error: {e}")

# Test simple test endpoint
simple_test_url = "http://localhost:5001/api/assets/simple-test"
print(f"Testing simple test URL: {simple_test_url}")

try:
    simple_test_response = requests.get(simple_test_url)
    print(f"Simple Test Status Code: {simple_test_response.status_code}")
    print(f"Simple Test Response: {simple_test_response.text}")
except Exception as e:
    print(f"Simple Test Error: {e}")

# Test detail-test endpoint
detail_test_url = "http://localhost:5001/api/assets/detail-test"
print(f"Testing detail-test URL: {detail_test_url}")

try:
    detail_test_response = requests.get(detail_test_url)
    print(f"Detail Test Status Code: {detail_test_response.status_code}")
    print(f"Detail Test Response: {detail_test_response.text}")
except Exception as e:
    print(f"Detail Test Error: {e}")

# Make request
url = f"http://localhost:5001/api/assets/detail/{asset_id}"
print(f"Testing URL: {url}")

try:
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Body: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"JSON Data: {json.dumps(data, indent=2)}")
    
except Exception as e:
    print(f"Error: {e}")
