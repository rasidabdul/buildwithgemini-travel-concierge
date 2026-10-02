# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import base64
import datetime
import json
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.cloud import firestore
from google.genai import types

# Hardcode project ID as string to prevent Agent Platform resolution issues
PROJECT_ID = "qwiklabs-gcp-02-9a8f822bd17b"
db = firestore.Client(project=PROJECT_ID)


def list_destinations(tag: str = "") -> str:
    """List travel destinations stored in Firestore, optionally filtering by a tag (e.g. 'culture', 'nature', 'food').

    Args:
        tag: Optional tag filter (e.g. 'culture', 'beach', 'nature').

    Returns:
        A list of available destinations with details.
    """
    collection_ref = db.collection("destinations")
    docs = collection_ref.stream()

    results = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        if tag:
            tags = [t.lower() for t in data.get("tags", [])]
            if tag.lower() not in tags:
                continue
        results.append(data)

    if not results:
        return f"No destinations found matching tag: '{tag}'." if tag else "No destinations found."
    return str(results)


def get_destination_details(destination_id: str) -> str:
    """Get full details for a specific travel destination from Firestore.

    Args:
        destination_id: The document ID of the destination (e.g. 'kyoto', 'paris', 'cape_town', 'reykjavik').

    Returns:
        Dictionary of destination details.
    """
    doc_ref = db.collection("destinations").document(destination_id)
    doc = doc_ref.get()
    if not doc.exists:
        return f"Destination '{destination_id}' not found."
    data = doc.to_dict()
    data["id"] = doc.id
    return str(data)


def save_destination(
    destination_id: str,
    name: str,
    country: str,
    description: str,
    best_season: str = "Year-round",
    tags: str = "culture,travel",
    rating: float = 4.5,
) -> str:
    """Save or update a travel destination entry in Firestore.

    Args:
        destination_id: Short unique key for the destination (e.g. 'tokyo', 'rome').
        name: Name of the destination city or region.
        country: Country where the destination is located.
        description: Brief summary of key attractions and highlights.
        best_season: Recommended time of year to visit.
        tags: Comma-separated list of tags (e.g. 'culture,food,historic').
        rating: Average rating score out of 5.0.

    Returns:
        Confirmation message of the save operation.
    """
    tag_list = [t.strip().lower() for t in tags.split(",") if t.strip()]
    doc_data = {
        "name": name,
        "country": country,
        "description": description,
        "best_season": best_season,
        "tags": tag_list,
        "rating": float(rating),
    }
    db.collection("destinations").document(destination_id).set(doc_data)
    return f"Successfully saved destination '{name}' ({destination_id}) to Firestore."


def fetch_weather(city: str) -> str:
    """Fetch live real-time weather information and current temperature for any travel destination.

    Args:
        city: Name of the city or destination to check weather for (e.g. 'Kyoto', 'Paris', 'Tokyo').

    Returns:
        Real-time weather summary including temperature and wind speed.
    """
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        req = Request(geo_url, headers={"User-Agent": "TravelConcierge/1.0"})
        with urlopen(req) as resp:
            geo_data = json.loads(resp.read().decode())

        if not geo_data.get("results"):
            return f"Could not find coordinates for '{city}'."

        loc = geo_data["results"][0]
        lat, lon = loc["latitude"], loc["longitude"]
        city_name = loc.get("name", city)
        country = loc.get("country", "")

        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        req_w = Request(weather_url, headers={"User-Agent": "TravelConcierge/1.0"})
        with urlopen(req_w) as resp:
            weather_data = json.loads(resp.read().decode())

        cw = weather_data.get("current_weather", {})
        temp_c = cw.get("temperature", "N/A")
        temp_f = round((temp_c * 9 / 5) + 32, 1) if isinstance(temp_c, (int, float)) else "N/A"
        wind = cw.get("windspeed", "N/A")

        return f"Current weather in {city_name}, {country}: {temp_c}°C ({temp_f}°F), Wind Speed: {wind} km/h."
    except Exception as e:
        return f"Error fetching live weather for {city}: {str(e)}"


import os
from urllib.parse import quote

def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """Convert travel budget and daily costs between different world currencies using real-time exchange rates.

    Args:
        amount: The monetary amount to convert (e.g. 100.0).
        from_currency: 3-letter currency code converting from (e.g. 'USD', 'EUR', 'GBP').
        to_currency: 3-letter currency code converting to (e.g. 'JPY', 'EUR', 'CAD').

    Returns:
        Converted amount and exchange rate date.
    """
    try:
        from_code = from_currency.strip().upper()
        to_code = to_currency.strip().upper()

        # Read optional API key from environment variable if provided
        api_key = os.getenv("CURRENCY_API_KEY") or os.getenv("FRANKFURTER_API_KEY")

        url = f"https://api.frankfurter.dev/v1/latest?amount={amount}&from={from_code}&to={to_code}"
        headers = {"User-Agent": "TravelConcierge/1.0"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        req = Request(url, headers=headers)
        with urlopen(req) as resp:
            data = json.loads(resp.read().decode())

        rates = data.get("rates", {})
        converted = rates.get(to_code)
        if converted is not None:
            rate_date = data.get("date", "latest")
            return f"{amount} {from_code} = {converted:.2f} {to_code} (Exchange rate as of {rate_date})."
        return f"Could not convert from {from_code} to {to_code}."
    except Exception as e:
        return f"Error converting currency from {from_currency} to {to_currency}: {str(e)}"


def geocode_address(address: str) -> str:
    """Geocode a physical address or landmark name into geographic coordinates (latitude and longitude).

    Args:
        address: Address or landmark name (e.g. 'Eiffel Tower, Paris' or 'Kyoto Station').

    Returns:
        Formatted address, latitude, and longitude.
    """
    try:
        api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if not api_key:
            return "Error: GOOGLE_MAPS_API_KEY is not configured in environment."

        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={quote(address)}&key={api_key}"
        req = Request(url)
        with urlopen(req) as resp:
            data = json.loads(resp.read().decode())

        if not data.get("results"):
            return f"No geocoding results found for '{address}'."

        first_res = data["results"][0]
        formatted_addr = first_res.get("formatted_address", address)
        location = first_res.get("geometry", {}).get("location", {})
        lat = location.get("lat")
        lng = location.get("lng")

        return f"Name/Query: '{address}', Formatted Address: '{formatted_addr}', Location: (Latitude: {lat}, Longitude: {lng})."
    except Exception as e:
        return f"Error geocoding address '{address}': {str(e)}"


def find_nearby_places(query: str) -> str:
    """Find places, attractions, restaurants, or hotels matching a search query using Google Places API (New).

    Args:
        query: Search query for places (e.g. 'museums in Kyoto', 'ramen near Tokyo Station').

    Returns:
        List of matching places with name, address, and coordinates.
    """
    try:
        api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if not api_key:
            return "Error: GOOGLE_MAPS_API_KEY is not configured in environment."

        url = "https://places.googleapis.com/v1/places:searchText"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location",
        }
        payload = {"textQuery": query}

        req = Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        with urlopen(req) as resp:
            data = json.loads(resp.read().decode())

        places = data.get("places", [])
        if not places:
            return f"No places found for query '{query}'."

        results = []
        for p in places[:5]:
            name = p.get("displayName", {}).get("text", "N/A")
            addr = p.get("formattedAddress", "N/A")
            loc = p.get("location", {})
            lat, lng = loc.get("latitude"), loc.get("longitude")
            results.append(f"Name: {name}, Address: {addr}, Location: ({lat}, {lng})")

        return "\n".join(results)
    except Exception as e:
        return f"Error searching places for '{query}': {str(e)}"


import os
import re
import time
from urllib.parse import quote

from google import genai
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.tools import ToolContext
from google.cloud import storage

GCS_BUCKET_NAME = "travel-concierge-media-qwiklabs-gcp-02-9a8f822bd17b"


async def generate_destination_image(
    prompt: str,
    destination_name: str,
    tool_context: ToolContext = None,
) -> str:
    """Generate a scenic travel photo preview or moodboard image for a destination using gemini-3.1-flash-lite-image in the global region.

    Saves the generated image as an ADK artifact for the Playground UI and uploads it directly to public Cloud Storage.

    Args:
        prompt: Detailed visual prompt describing the scene, lighting, style, and travel landmark.
        destination_name: Short name of the destination (e.g., 'kyoto', 'paris', 'cape_town').
        tool_context: Optional ADK ToolContext passed automatically by the framework.

    Returns:
        Public GCS HTTPS URL of the uploaded image.
    """
    try:
        # Initialize Google GenAI client for global region image generation
        client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")

        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-image",
            contents=prompt,
            config=types.GenerateContentConfig(response_modalities=["IMAGE"]),
        )

        image_bytes = None
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data and part.inline_data.data:
                    image_bytes = part.inline_data.data
                    break

        if not image_bytes:
            return f"Error: No image bytes generated for '{destination_name}'."

        # Clean destination name for filenames
        clean_name = re.sub(r"[^a-zA-Z0-9_-]", "_", destination_name.lower().strip())
        filename = f"{clean_name}_{int(time.time())}.png"

        # 1. Save artifact with tool_context for Playground UI
        if tool_context:
            artifact_part = types.Part.from_bytes(data=image_bytes, mime_type="image/png")
            res = tool_context.save_artifact(filename=filename, artifact=artifact_part)
            if hasattr(res, "__await__"):
                await res

        # 2. Upload image bytes directly to public GCS bucket (no local file)
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(f"destination_previews/{filename}")
        blob.upload_from_string(image_bytes, content_type="image/png")

        public_url = f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/destination_previews/{filename}"
        return f"Successfully generated scenic image for '{destination_name}'. Public image URL: {public_url}"
    except Exception as e:
        return f"Error generating image for '{destination_name}': {str(e)}"


async def generate_destination_video(
    prompt: str,
    destination_name: str,
    tool_context: ToolContext = None,
) -> str:
    """Generate a short video preview for a travel destination or landmark using Google's Omni model (gemini-omni-flash-preview) in the global region.

    Saves the generated video as an ADK artifact for the Playground UI and uploads it to public Cloud Storage.

    Args:
        prompt: Visual description of the video scene to generate (e.g., 'Cinematic panning video of Kyoto cherry blossoms falling near a shrine').
        destination_name: Short name of the destination (e.g., 'kyoto', 'paris', 'tokyo').
        tool_context: Optional ADK ToolContext passed automatically by the framework.

    Returns:
        Public GCS HTTPS URL of the uploaded video.
    """
    try:
        # Initialize Google GenAI client for global region video generation using Omni model
        client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")

        interaction = client.interactions.create(
            model="gemini-omni-flash-preview",
            input=prompt,
        )

        video_bytes = None
        if hasattr(interaction, "output_video") and interaction.output_video:
            data = interaction.output_video.data
            if isinstance(data, str):
                video_bytes = base64.b64decode(data)
            else:
                video_bytes = data

        if not video_bytes:
            return f"Error: No video bytes generated for '{destination_name}'."

        clean_name = re.sub(r"[^a-zA-Z0-9_-]", "_", destination_name.lower().strip())
        filename = f"{clean_name}_{int(time.time())}.mp4"

        # 1. Save artifact with tool_context for Playground UI
        if tool_context:
            artifact_part = types.Part.from_bytes(data=video_bytes, mime_type="video/mp4")
            res = tool_context.save_artifact(filename=filename, artifact=artifact_part)
            if hasattr(res, "__await__"):
                await res

        # 2. Upload video bytes directly to public GCS bucket (no local file)
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(f"destination_videos/{filename}")
        blob.upload_from_string(video_bytes, content_type="video/mp4")

        public_url = f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/destination_videos/{filename}"
        return f"Successfully generated video preview for '{destination_name}'. Public video URL: {public_url}"
    except Exception as e:
        return f"Error generating video for '{destination_name}': {str(e)}"


# Configure AgentEngineSandboxCodeExecutor for safe Python code execution
code_executor = None
metadata_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "deployment_metadata.json")
if os.path.exists(metadata_path):
    try:
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
            agent_engine_id = metadata.get("remote_agent_runtime_id")
            if agent_engine_id:
                code_executor = AgentEngineSandboxCodeExecutor(agent_engine_resource_name=agent_engine_id)
    except Exception as e:
        print(f"Warning: Could not initialize AgentEngineSandboxCodeExecutor from metadata: {e}")

if not code_executor:
    code_executor = AgentEngineSandboxCodeExecutor(
        agent_engine_resource_name="projects/514886372165/locations/us-central1/reasoningEngines/6704786172050145280"
    )

# Memory Bank configuration for long-term cross-session memory
from google.adk.agents.callback_context import CallbackContext
from google.adk.memory import VertexAiMemoryBankService
from google.adk.tools.preload_memory_tool import PreloadMemoryTool

MEMORY_BANK_ID = "6704786172050145280"


async def generate_memories_callback(callback_context: CallbackContext):
    try:
        await callback_context.add_session_to_memory()
    except Exception as e:
        print(f"Memory Bank callback status: {e}")
    return None



memory_service = VertexAiMemoryBankService(
    project=PROJECT_ID,
    location="us-central1",
    agent_engine_id=MEMORY_BANK_ID,
)


def memory_service_builder():
    return VertexAiMemoryBankService(
        project=PROJECT_ID,
        location="us-central1",
        agent_engine_id=MEMORY_BANK_ID,
    )



# A2UI configuration for rich UI rendering in ADK Web
from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager
from app.a2ui_utils import a2ui_callback

schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

a2ui_instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are Travel Concierge, an expert travel assistant. "
        "You help users explore travel destinations, convert currencies, look up place coordinates, "
        "find nearby attractions and restaurants, generate scenic AI image and video previews, run calculations safely via Python code execution, check live weather, and plan trips. "
        "You actively track, remember, and recall all past travel destinations (cities, countries, regions, landmarks) that the user has already visited, along with their travel preferences and style."
    ),
    workflow_description="Analyze the request and return structured UI when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        "{\"Image\": {\"url\": {\"literalString\": \"https://...\"}}}. Never point an "
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=a2ui_instruction,
    tools=[
        list_destinations,
        get_destination_details,
        save_destination,
        fetch_weather,
        convert_currency,
        geocode_address,
        find_nearby_places,
        generate_destination_image,
        generate_destination_video,
        PreloadMemoryTool(),
    ],
    after_agent_callback=generate_memories_callback,
    after_model_callback=a2ui_callback,
    code_executor=code_executor,
)


app = App(
    root_agent=root_agent,
    name="app",
)








