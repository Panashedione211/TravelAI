#main.py - FastAPI application for TravelAI
from fastapi import FastAPI, Request  # Create the app and get HTTP request info in routes
from fastapi.middleware.cors import CORSMiddleware  # Let browser pages from other origins talk to this API
from fastapi.staticfiles import StaticFiles  # Serve static files like CSS and JS to the browser
from fastapi.templating import Jinja2Templates  # Show HTML pages using Jinja2 templates (Jinja2 lets us use variables and logic in HTML)
from database import engine
from models import Base
from routers import auth, trips
import os

# create database tables if they don't exist
Base.metadata.create_all(bind=engine)

# starts the web application
app = FastAPI(title="TravelAI API")

# CORS middleware to allow frontend to call this API
# Cors = Cross-origin resource sharing, it controls whether a web page from one site can request data from another 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and templates from Frontend folder
# finds the Frontend folder relative to this file, then serves static files from there and sets up Jinja2 templates to read from there too
# links backend to frontend so we can serve the HTML pages and static assets (CSS/JS) for the UI
FRONTEND = os.path.join(os.path.dirname(__file__), "..", "Frontend")
app.mount("/static", StaticFiles(directory=os.path.join(FRONTEND, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(FRONTEND, "templates"))

# API routers
#organzies API endpoints into groups auth and trips and adds prefixes to ther urls, so all auth routes start with the correct route
app.include_router(auth.router)
app.include_router(trips.router)


# ── Page routes ───────────────────────────────────────────────────────────────
#returns the corresponding HTML page for each route, these are the pages the user sees when they visit these urls in their browser.
@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/signup")
def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@app.get("/dashboard")
def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/questionnaire")
def questionnaire_page(request: Request):
    return templates.TemplateResponse("questionnaire.html", {"request": request})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
