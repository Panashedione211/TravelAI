# TravelAI ✈️

An AI-powered travel planning app that generates personalized itineraries and interactive maps based on your travel preferences. Built for a Microsoft hackathon using Azure AI Foundry.

## Demo Video

▶️ [Watch the demo on YouTube](https://youtu.be/HquClLOQOqQ)

## How It Works

1. Sign up and log in
2. Answer 6 quick questions about your trip (destination, days, budget, travel style, pace, group type)
3. Azure AI generates a personalized day-by-day itinerary
4. View your plan on an interactive map with color-coded pins per day
5. Use the AI chat box to tweak the plan — changes update the map and itinerary in real time

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML, CSS, JavaScript, Leaflet.js |
| Backend | Python, FastAPI |
| Database | SQLite via SQLAlchemy |
| AI | Azure AI Foundry (gpt-4.1-mini) |
| Knowledge Base | Azure AI Search + Wikivoyage API (Foundry IQ) |
| Maps | Leaflet.js + OpenStreetMap |
| Geocoding | OpenStreetMap Nominatim |
| Auth | JWT via python-jose + passlib |

## Project Structure

```
TravelAI/
├── Backend/
│   ├── main.py               # FastAPI app entry point
│   ├── database.py           # SQLite connection setup
│   ├── models.py             # Database tables (User, Trip, ItineraryStop)
│   ├── schemas.py            # Request/response data shapes
│   ├── auth_utils.py         # JWT and password hashing
│   ├── foundry.py            # Azure AI Foundry integration + Nominatim geocoding
│   ├── search.py             # Azure AI Search + Wikivoyage knowledge base (Foundry IQ)
│   └── routers/
│       ├── auth.py           # Register, login, me
│       ├── trips.py          # Trip CRUD and stops
│       └── itinerary.py      # AI generation and chat update endpoints
├── Frontend/
│   ├── static/
│   │   ├── css/style.css
│   │   └── js/main.js
│   └── templates/
│       ├── base.html
│       ├── login.html
│       ├── signup.html
│       ├── dashboard.html
│       ├── questionnaire.html
│       └── trip_detail.html  # Map + itinerary + chat
└── .gitignore
```

## Architecture

```
User (Browser)
    │
    ▼
FastAPI Backend
    ├── routers/auth.py       — JWT login/register
    ├── routers/trips.py      — Trip CRUD + stops
    ├── routers/itinerary.py  — Generate + chat endpoints
    ├── search.py             ──────────────────────────────┐
    │       │                                               │
    │       ▼                                               ▼
    │  Wikivoyage API                            Azure AI Search
    │  (free travel guides)          ◄──────     (Foundry IQ index)
    │                                            travelai-guides
    └── foundry.py
            │  (injects Wikivoyage context)
            ▼
     Azure AI Foundry
     gpt-4.1-mini
     (generates JSON itinerary)
            │
            ▼
     Nominatim (OpenStreetMap)
     (real GPS coordinates per stop)
            │
            ▼
     Leaflet.js Map
     (color-coded pins per day)
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

Edit `.env` with your values:

```
SECRET_KEY=your-secret-key
FOUNDRY_API_KEY=your-azure-api-key
FOUNDRY_ENDPOINT=https://your-resource.services.ai.azure.com/openai/v1/chat/completions
FOUNDRY_DEPLOYMENT=gpt-4.1-mini
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_SEARCH_KEY=your-search-admin-key
AZURE_SEARCH_INDEX=travelai-guides
```

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
| POST | `/api/trips/{id}/generate` | Generate AI itinerary |
| POST | `/api/trips/{id}/chat` | Update itinerary via chat |

## Build Phases

- [x] **Phase 1** — App foundation, database, auth, base HTML pages
- [x] **Phase 2** — Azure AI Foundry integration, itinerary generation, Leaflet map with colored pins
- [x] **Phase 3** — AI chat box that updates the itinerary and map in real time
- [x] **Phase 4** — Foundry IQ: Azure AI Search + Wikivoyage knowledge base grounding
