from google import genai
from pydantic import BaseModel
from typing import List
import json

destinations = [
    {"id": "186525", "name": "Edinburgh, United Kingdom"},
    {"id": "187879", "name": "Sardinia, Italy"},
    {"id": "187514", "name": "Madrid, Spain"},
    {"id": "187479", "name": "Tenerife, Spain"},
    {"id": "187895", "name": "Florence, Italy"},
    {"id": "189433", "name": "Santorini, Greece"},
    {"id": "274887", "name": "Budapest, Hungary"},
    {"id": "189180", "name": "Porto, Portugal"},
    {"id": "186605", "name": "Dublin, Ireland"},
    {"id": "274707", "name": "Prague, Czech Republic"},
    {"id": "189449", "name": "Rhodes, Greece"},
    {"id": "190320", "name": "Island of Malta, Malta"},
    {"id": "297983", "name": "Goreme, Cappadocia, Turkey"},
    {"id": "274772", "name": "Krakow, Poland"},
    {"id": "189970", "name": "Reykjavik, Iceland"},
]


class MonthTemp(BaseModel):
    month: int
    temp: int


class Destination(BaseModel):
    id: str
    name: str
    description: str
    climate: str
    avg_monthly_temp: List[MonthTemp]
    best_time_to_visit: str
    avg_daily_cost_range: List[int]
    tags: List[str]


system_prompt = """
You are a travel knowledge assistant that will help create a realistic profile of a destination based on your pre trained knowledge.
You will be provided with a name of a destination and you need to generate a profile for it.
The profile should include:
- ID: Already provided
- Name: Already provided
- Description: A detailed description of the destination
- Climate: The climate of the destination explained in detail
- Best time to visit: The best time of year to visit the destination described in detail
- Average monthly temperature range: The average monthly temperature range in Celsius [month, temp]. The month and temp are integers.
- Average daily cost range: The average daily cost range in USD per person (please be realistic)
- Tags: A list of tags that describe the destination
All of the generated values should be based on your pre trained knowledge and should reflect the real world values.
Please don't generate random values and do not hallucinate.

---

Here is the input:
Destination Name: {destination_name}
Destination ID: {destination_id}
"""
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])


def generate_destination(destination_name, destination_id):
    # Use double curly braces to escape the JSON curly braces in the prompt
    prompt = system_prompt.replace("{destination_name}", destination_name).replace(
        "{destination_id}", destination_id
    )
    response = client.models.generate_content(
        model="models/gemini-2.5-pro-exp-03-25",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": Destination,
        },
    )
    return response.text


json_destinations = []

for destination in destinations:
    destination_data = generate_destination(destination["name"], destination["id"])
    print(destination_data)
    json_destinations.append(json.loads(destination_data))

# save destinations to file
with open("12345destinations.json", "w") as f:
    json.dump(json_destinations, f, indent=4)
