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


def build_user_prompt(trip):
    # This function takes the trip details and formats them into a user prompt that can be sent to Foundry.
    return f"""Plan a {trip.days}-day trip to {trip.destination}.
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
        return parse_foundry_response(content)
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
    
def chat_with_trip(trip, stops, message):
    """Send a user message about a specific trip and return the AI reply."""
    stops_text = "\n".join(
        f"Day {s['day_number']} Stop {s['stop_number']}: {s['name']} — {s['description']} (~${s['estimated_cost']})"
        for s in stops
    )
    system = f"""You are a travel assistant helping the user adjust their trip to {trip.destination}.
Here is their current itinerary:
{stops_text}

Only answer questions or make suggestions related to this trip. Be concise and helpful."""

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
        "max_tokens": 500,
    }
    with httpx.Client(timeout=60.0) as client:
        response = client.post(FOUNDRY_ENDPOINT, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


# parses ai response, extracts JSON, and returns it as a Python list of dicts
def parse_foundry_response(response_text):
    # This function extracts the JSON array from the Foundry response, even if there is extra text around it.
    json_array_match = re.search(r"\[.*\]", response_text, re.DOTALL)
    if not json_array_match:
        raise ValueError("No JSON array found in Foundry response")
    return json.loads(json_array_match.group(0))

