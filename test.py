import requests

r = requests.get("http://localhost:3000")
print(r.status_code)