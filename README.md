# TravelAI ✈️

An AI-powered travel planning app that generates personalized itineraries and interactive maps based on your travel preferences.

## How It Works

1. Sign up and log in
2. Answer 6 quick questions about your trip
3. AI generates a personalized itinerary
4. View your plan on an interactive map with numbered pinpoints
5. Use the AI chatbox to tweak the plan

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML, CSS, JavaScript, Leaflet.js |
| Backend | Python, FastAPI |
| Database | SQLite |
| AI | Microsoft Foundry |
| Maps | OpenStreetMap |

## Project Structure

```
TravelAI/
├── Backend/
│   ├── main.py               # FastAPI app entry point
│   ├── database.py           # SQLite connection setup
│   ├── models.py             # Database tables (User, Trip, ItineraryStop)
│   ├── schemas.py            # Request/response data shapes
│   ├── auth_utils.py         # JWT and password hashing
│   └── routers/
│       ├── auth.py           # Register, login, me
│       └── trips.py          # Trip CRUD and stops
├── Frontend/
│   ├── static/
│   │   ├── css/style.css
│   │   └── js/main.js
│   └── templates/
│       ├── base.html
│       ├── login.html
│       ├── signup.html
│       ├── dashboard.html
│       └── questionnaire.html
└── .gitignore
```

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/Panashedione211/TravelAI.git
cd TravelAI/Backend
```

### 2. Create a virtual environment

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1   # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env` and set your own `SECRET_KEY`.

### 5. Run the app

```bash
python main.py
```

Open your browser and go to `http://localhost:8000`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Create account |
| POST | `/api/auth/login` | Login, returns JWT |
| GET | `/api/auth/me` | Get current user |
| POST | `/api/trips/` | Create a trip |
| GET | `/api/trips/` | List all trips |
| GET | `/api/trips/{id}` | Get single trip |
| DELETE | `/api/trips/{id}` | Delete a trip |
| GET | `/api/trips/{id}/stops` | Get itinerary stops |

## Build Phases

- [x] **Phase 1** — App foundation, database, auth, base HTML pages
- [ ] **Phase 2** — Microsoft Foundry AI integration, itinerary generation, Leaflet map
- [ ] **Phase 3** — AI chatbox tweaks, stop editing
