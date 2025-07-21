import requests

url = "http://localhost:5001/api/assets/detail/aa0e8400-e29b-41d4-a716-446655440001"
print(f"Testing URL: {url}")

try:
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Error: {e}")
