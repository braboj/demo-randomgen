import requests

# Generate numbers from a custom distribution, supplied per request via
# repeated `value` / `probability` query parameters (the service is stateless;
# the old POST /api/config endpoint has been removed).
url = 'http://127.0.0.1:5000/api/v1/randomgen'
params = {
    'numbers': 1000,
    'value': [1, 2, 3],
    'probability': [0.2, 0.2, 0.6],
}

# Send a GET request
response = requests.get(url, params=params)

# Check the response
if response.status_code == 200:
    print("Response from server:", response.json())
else:
    print("Error:", response.status_code, response.text)
