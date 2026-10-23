"""Fills the event to capacity, then tries to over-register.
Run the server first (uvicorn main:app --reload), delete registrations.db for a clean start."""
import requests

URL = "http://127.0.0.1:8000/register"
for i in range(52):
    r = requests.post(URL, json={"name": f"Student {i}", "email": f"s{i}@test.com"})
    print(i, r.status_code, r.json())
