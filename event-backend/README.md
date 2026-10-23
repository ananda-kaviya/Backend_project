# Event Registration Backend - Celestius Recruitment Task

A simple backend for the **Backend Development Workshop** (20 October 2026, capacity 50).
Built with **Python, FastAPI and SQLite**.

## Setup

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
uvicorn main:app --reload
```

Open http://127.0.0.1:8000/docs to try every endpoint in the browser.

## Endpoints

| Method | Route | Description |
|---|---|---|
| POST | `/register` | Register a student |
| GET | `/registrations` | List all registrations and seats filled |
| GET | `/registrations/{id}` | View one registration |

### Example request

```json
POST /register
{ "name": "Priya", "email": "priya@example.com", "college_department": "CSE" }
```

### Responses

| Situation | Status | Message |
|---|---|---|
| Success | 201 | Registration successful |
| Duplicate email | 409 | This email is already registered |
| Event full (50/50) | 409 | Event is full |
| Missing/invalid data | 422 | Validation details |
| ID not found | 404 | Registration not found |

## Design decisions

- **Email is UNIQUE** in the database, so duplicates are blocked even if the code has a bug.
- **Capacity check and insert happen in one transaction** (`BEGIN IMMEDIATE`), so two simultaneous requests cannot both take the last seat.
- **Pydantic** validates input automatically (name required, email must be valid).
- Emails are stored in lowercase so `A@x.com` and `a@x.com` count as the same person.

## Testing the capacity limit

Delete `registrations.db`, start the server, then run `python test_full.py`.
Registrations 0-49 return 201; 50 and 51 return 409 "Event is full".
