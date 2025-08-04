import requests

url = "http://localhost:5001/api/assets/detail/1158274a-e29b-41d4-a716-446655440001"
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc1MjExNDE3NCwianRpIjoiNWY5ZjhiMTctMGY0YS00NDk3LWJjZDUtYjI1YzIzNTYyZjEyIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6Ijc3MGU4NDAwLWUyOWItNDFkNC1hNzE2LTQ0NjY1NTQ0MDAwMSIsIm5iZiI6MTc1MjExNDE3NCwicm9sZSI6InN1cGVyYWRtaW4iLCJjbGllbnRfaWQiOm51bGwsInNpdGVfaWRzIjpbXSwibmFtZSI6IkJlbmphbWluIEFoYXJvbm92IiwiZW1haWwiOiJiYUBsYW5ldC5teCJ9.OHjQeIMlmSQRCb-J0q3t8eq31Lmso40hMArZnfZZ740",
    "Content-Type": "application/json"
}
print(f"Testing URL: {url}")

try:
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Error: {e}")
