import datetime
import zoneinfo
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
import os
from dotenv import load_dotenv
import requests
from elevenlabs.client import ElevenLabs
from elevenlabs.play import play
from elevenlabs import save
from google.adk.tools.tool_context import ToolContext
from google.adk.tools import google_search
from .prompt.prompt import agent_instruction
from pathlib import Path
import uuid

# Load environment variables from .env file
load_dotenv()

from typing import Optional, List, Dict

def get_weather(city: str, tool_context: ToolContext) -> dict:
    """Retrieves weather, converts temp unit based on session state."""
    print(f"--- Tool: get_weather_stateful called for {city} ---")

    # --- Read preference from state ---
    preferred_unit = tool_context.state.get("user_preference_temperature_unit", "Celsius") # Default to Celsius
    print(f"--- Tool: Reading state 'user_preference_temperature_unit': {preferred_unit} ---")

    city_normalized = city.lower().replace(" ", "")

    # Mock weather data (always stored in Celsius internally)
    mock_weather_db = {
        "newyork": {"temp_c": 25, "condition": "sunny"},
        "london": {"temp_c": 15, "condition": "cloudy"},
        "tokyo": {"temp_c": 18, "condition": "light rain"},
    }

    if city_normalized in mock_weather_db:
        data = mock_weather_db[city_normalized]
        temp_c = data["temp_c"]
        condition = data["condition"]

        # Format temperature based on state preference
        if preferred_unit == "Fahrenheit":
            temp_value = (temp_c * 9/5) + 32 # Calculate Fahrenheit
            temp_unit = "°F"
        else: # Default to Celsius
            temp_value = temp_c
            temp_unit = "°C"

        report = f"The weather in {city.capitalize()} is {condition} with a temperature of {temp_value:.0f}{temp_unit}."
        result = {"status": "success", "report": report}
        print(f"--- Tool: Generated report in {preferred_unit}. Result: {result} ---")

        # Example of writing back to state (optional for this tool)
        tool_context.state["last_city_checked_stateful"] = city
        print(f"--- Tool: Updated state 'last_city_checked_stateful': {city} ---")

        return result
    else:
        # Handle city not found
        error_msg = f"Sorry, I don't have weather information for '{city}'."
        print(f"--- Tool: City '{city}' not found. ---")
        return {"status": "error", "error_message": error_msg}


def say_hello(name: Optional[str] = None) -> str: 
    """Provides a simple greeting. If a name is provided, it will be used.

    Args:
        name (str, optional): The name of the person to greet. Defaults to a generic greeting if not provided.

    Returns:
        str: A friendly greeting message.
    """
    if name:
        greeting = f"Hello, {name}!"
        print(f"--- Tool: say_hello called with name: {name} ---")
    else:
        greeting = "Hello there!" # Default greeting if name is None or not explicitly passed
        print(f"--- Tool: say_hello called without a specific name (name_arg_value: {name}) ---")
    return greeting

def say_goodbye() -> str:
    """Provides a simple farewell message to conclude the conversation."""
    print(f"--- Tool: say_goodbye called ---")
    return "Goodbye! Have a great day."

def get_current_time(city: str) -> dict:
    city_normalized = city.strip().replace(" ", "_").lower()
    matching_zones = [
        tz for tz in zoneinfo.available_timezones()
        if city_normalized in tz.lower()
    ]

    if not matching_zones:
        return {
            "status": "error",
            "error_message": (
                f"Sorry, I don't have timezone information for {city}."
            ),
        }

    # Pick the best match (first one)
    tz_identifier = matching_zones[0]
    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)

    report = (
        f'The current time in {city} is {now.strftime("%Y-%m-%d %H:%M:%S")} '
        f'(Timezone: {tz_identifier})'
    )
    return {"status": "success", "report": report}

#def get_current_time(city: str) -> dict:
#    """Get the current time in a city."""
#    city_timezones = {
#        "new york": "America/New_York",
#        "london": "Europe/London",
#        "tokyo": "Asia/Tokyo",
#        "paris": "Europe/Paris"
#    }
#    if city.lower() in city_timezones:
#        try:
#            tz = ZoneInfo(city_timezones[city.lower()])
#            now = datetime.datetime.now(tz)
#            return {
#                "status": "success",
#                "report": f"The current time in {city} is {now.strftime('%Y-%m-%d %H:%M:%S %Z')}"
#            }
#        except Exception:
#            pass
#            return {
#                "status": "error",
#                 "error_message": f"Time information for '{city}' unavailable."
#    }

# ----- Example of a Function tool -----
def get_current_date() -> dict:
    """
    Get the current date in the format YYYY-MM-DD
    """
    return {"current_date": datetime.now().strftime("%Y-%m-%d")}


# ----- Example of a Built-in Tool -----
search_agent = Agent(
    model=os.getenv("AGENT_MODEL", "gemini-2.5-flash"),
    name="search_agent",
    instruction="""
    You're a specialist in Google Search.
    """,
    tools=[google_search],
)

def translate_response(originalText: str, lang: str) -> dict:
    try:
        api_key = os.getenv('GOOGLE_API_KEY')
        base_url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent'
        data = {"contents": [{
            "parts":[{"text": f"Convert the following text in {lang}: {originalText}"}]
            }]
        }
        headers = {'content-type': 'application/json'}
        params = { 'key': api_key }
        api_response = requests.post(base_url, json=data, params=params, headers=headers );
        return {"status": "success", "report": api_response.json()}
    except e:
        print(f"Error fetching translation data: {e}")
        return None
    
def get_voice_response(text: str, voice_id: str = "JBFqnCBsd6RMkjVDRZzb"):
    try:
        print(f"Calling ElevenLabs Text2Speech service")
        client = ElevenLabs(
            api_key=os.getenv("ELEVENLABS_API_KEY"),
        )
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        output_file_data = output_dir / f"{uuid.uuid4()}.mp3"

        audio = client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
        )
        save(audio, output_file_data)
        print(f"saved at:`{output_file_data}`")
        # Return the path of the saved audio file
        return { "result": {"content":[{"text":f"saved at:{output_file_data}"}]} }
    except APIError as e:
        print(f"Error fetching translation data: {e}")
        return {
            "status": "voice management failure",
        }

root_agent = Agent(
    name = "support_info_agent",
    model=os.getenv("AGENT_MODEL","gemini-2.5-flash"),
    description="Agent to answer questions about time, weather, translate text, provide voice responses, and fetch news from Reddit. It can also save information as a PDF.",
    instruction=agent_instruction,
    tools=[get_weather, get_current_time, translate_response, get_voice_response],
)