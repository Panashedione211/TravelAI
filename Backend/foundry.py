import os
import json
import re
import httpx
from dotenv import load_dotenv

load_dotenv()

FOUNDRY_API_KEY    = os.getenv("FOUNDRY_API_KEY", "")
FOUNDRY_ENDPOINT   = os.getenv("FOUNDRY_ENDPOINT", "")
FOUNDRY_DEPLOYMENT = os.getenv("FOUNDRY_DEPLOYMENT", "gpt-4.1-mini")

SYSTEM_PROMPT = """You are a travel planning assistant that creates detailed itineraries based on user preferences.
You will be given a set of user preferences and constraints, and your task is to generate a comprehensive itinerary that includes daily stops with descriptions, locations, and estimated costs.
The itinerary should be organized by day and stop number, and should include a variety of activities that match the user's interests while respecting their budget and time constraints.
Be creative and suggest unique experiences that the user might not find on their own, but also ensure that the suggestions are realistic and feasible given the user's preferences and constraints.

Pace rules:
- relaxed: 2-3 stops per day
- balanced: 3-4 stops per day
- packed: 5-6 stops per day

Budget rules:
- budget: prioritize free or low-cost attractions
- mid-range: mix of free and paid experiences
- luxury: include upscale restaurants, hotels, and premium experiences

Group rules:
- family: include kid-friendly activities
- solo: include social spots and safe areas
- couple: include romantic experiences
- friends: include group-friendly activities

You MUST respond with a valid JSON array and nothing else. No markdown, no explanation, no extra text.
Each item must have exactly these fields:
{
  "day_number": 1,
  "stop_number": 1,
  "name": "Stop Name",
  "description": "A brief description of the stop and why it fits the traveler.",
  "lat": 0.0,
  "lng": 0.0,
  "estimated_cost": 0.0
}"""


def geocode_stop(name: str, destination: str):
    """Look up real coordinates for a stop by searching its name + destination."""
    try:
        with httpx.Client(timeout=10.0) as client:
            r = client.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": f"{name}, {destination}", "format": "json", "limit": 1},
                headers={"User-Agent": "TravelAI/1.0"},
            )
        data = r.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception:
        pass
    return None, None


def geocode_stops(stops: list, destination: str) -> list:
    """Replace AI-generated coordinates with real ones from Nominatim."""
    for stop in stops:
        lat, lng = geocode_stop(stop.get("name", ""), destination)
        if lat and lng:
            stop["lat"] = lat
            stop["lng"] = lng
    return stops


def get_destination_coords(destination: str):
    """Look up the approximate lat/lng of a destination using OpenStreetMap Nominatim."""
    try:
        with httpx.Client(timeout=10.0) as client:
            r = client.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": destination, "format": "json", "limit": 1},
                headers={"User-Agent": "TravelAI/1.0"},
            )
        data = r.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception:
        pass
    return None, None


def build_user_prompt(trip):
    lat, lng = get_destination_coords(trip.destination)
    coords_hint = f"\nAll stops must be real places located in or near {trip.destination}." if lat else ""
    return f"""Plan a {trip.days}-day trip to {trip.destination}.{coords_hint}
Traveler profile:
- Budget: {trip.budget}
- Travel style: {trip.travel_style}
- Pace: {trip.pace}
- Group type: {trip.group_type}

return only json array of stops, no extra text. """


def generate_itinerary(trip):
    """This function calls the Foundry API to generate an itinerary 
    based on the trip details. if no api key or endpint is set 
    returns a mock itinerary for testing purposes. """
    if not FOUNDRY_API_KEY or not FOUNDRY_ENDPOINT:
        print("Using mock itinerary")
        return mock_itinerary(trip)
    # api key and endpoint are set, call Foundry to get real itinerary
    headers = {
        "api-key": FOUNDRY_API_KEY,
        "Content-Type": "application/json",
    }
    # builds the request with the system and user prompts
    payload = {
        "model": FOUNDRY_DEPLOYMENT,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(trip)},
        ],
        "temperature": 0.7,
        "max_tokens": 4000,
    }
    import time
    for attempt in range(3):
        with httpx.Client(timeout=120.0) as client:
            response = client.post(FOUNDRY_ENDPOINT, headers=headers, json=payload)
        if response.status_code == 429:
            wait = 60 * (attempt + 1)
            print(f"[Foundry] 429 rate limit — waiting {wait}s before retry {attempt + 1}/3")
            time.sleep(wait)
            continue
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        stops = parse_foundry_response(content)
        return geocode_stops(stops, trip.destination)
    raise Exception("Rate limit exceeded after 3 retries. Wait a few minutes and try again.")
    
def mock_itinerary(trip):
    # This is a mock itinerary generator that returns a fixed set of stops for testing purposes.
    return [
        {
            "day_number": 1,
            "stop_number": 1,
            "name": "Mock Stop 1",
            "description": "A fun activity to start your trip.",
            "lat": 40.7128,
            "lng": -74.0060,
            "estimated_cost": 0.0,
        },
        {
            "day_number": 1,
            "stop_number": 2,
            "name": "Mock Stop 2",
            "description": "A great place to eat and relax.",
            "lat": 40.7138,
            "lng": -74.0070,
            "estimated_cost": 20.0,
        },
    ]
    
def chat_update_trip(trip, stops, message):
    """Takes the user's change request and returns a fully updated stop list as JSON."""
    stops_json = json.dumps(stops, indent=2)
    lat, lng = get_destination_coords(trip.destination)
    coords_hint = f"\nAll stops must be real places located in or near {trip.destination}." if lat else ""
    system = f"""You are a travel planning assistant. The user has an existing itinerary for a trip to {trip.destination}.{coords_hint}
They want to make a change to it. Apply their requested change and return the COMPLETE updated itinerary as a JSON array.

Current itinerary:
{stops_json}

Rules:
- Return ONLY a valid JSON array, no extra text or markdown
- Keep all stops that are not affected by the change
- Each stop must have: day_number, stop_number, name, description, lat, lng, estimated_cost
- lat/lng must be real coordinates for the location"""

    headers = {
        "api-key": FOUNDRY_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "model": FOUNDRY_DEPLOYMENT,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": message},
        ],
        "temperature": 0.7,
        "max_tokens": 4000,
    }
    with httpx.Client(timeout=120.0) as client:
        response = client.post(FOUNDRY_ENDPOINT, headers=headers, json=payload)
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    stops = parse_foundry_response(content)
    return geocode_stops(stops, trip.destination)


# parses ai response, extracts JSON, and returns it as a Python list of dicts
def parse_foundry_response(response_text):
    print("[Foundry raw response]", repr(response_text[:500]))
    # Strip markdown code fences if present
    text = re.sub(r"```(?:json)?", "", response_text).strip()
    json_array_match = re.search(r"\[.*\]", text, re.DOTALL)
    if not json_array_match:
        raise ValueError("No JSON array found in Foundry response")
    result = json.loads(json_array_match.group(0))
    print("[Foundry parsed]", type(result), result[:1] if result else [])
    if not isinstance(result, list) or not all(isinstance(s, dict) for s in result):
        raise ValueError(f"Foundry response is not a list of stop objects, got: {[type(s) for s in result[:3]]}")
    return result

