import requests

# Endpoint URL
url = 'http://127.0.0.1:5000/api/v1/randomgen'

# Generate numbers from a custom distribution via query parameters
response = requests.get(url, params={
    'numbers': 10,
    'value': [1, 2, 3],
    'probability': [0.2, 0.2, 0.6],
})
if response.status_code == 200:
    print("Custom distribution:", response.json())
else:
    print("Error:", response.status_code, response.text)

# Generate numbers from the built-in default distribution
response = requests.get(url, params={'numbers': 10})
if response.status_code == 200:
    print("Default distribution:", response.json())
else:
    print("Error:", response.status_code, response.text)
