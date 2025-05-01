import os
import re
import weaviate
from weaviate.auth import Auth
from weaviate.agents.query import QueryAgent
from weaviate_agents.utils import print_query_agent_response
from dotenv import load_dotenv

load_dotenv()


def connect_to_weaviate():
    try:
        headers = {
            "X-OpenAI-Api-Key": os.environ["OPENAI_API_KEY"],
        }
        client = weaviate.connect_to_weaviate_cloud(
            cluster_url=os.environ["WEAVIATE_URL"],
            auth_credentials=Auth.api_key(os.environ["WEAVIATE_API_KEY"]),
            headers=headers,
        )
        if client.is_ready():
            print("Weaviate is ready!")
        return client
    except Exception as e:
        print(f"Error: {e}")
        return None


def find_destination_id(client, destination_name):
    """Search for a destination in the Destinations collection and return its ID."""
    try:
        response = client.collections.get("Destinations").query.near_text(
            query=destination_name,
            limit=1
        )
        
        if response.objects:
            destination_obj = response.objects[0]
            destination_id = destination_obj.properties.get("destination_id")
            destination_name = destination_obj.properties.get("name")
            print(f"Found destination: {destination_name} with ID: {destination_id}")
            return str(destination_id), destination_name
        else:
            print(f"No destination found for: {destination_name}")
            return None, None
    except Exception as e:
        print(f"Error searching for destination: {e}")
        return None, None


def create_dynamic_system_prompt(destination_id=None, destination_name=None):
    """Create a system prompt with destination ID if available."""
    base_prompt = """
    You are a helpful travel planning assistant. Create personalized itineraries based on user preferences. You have access to two collections: Attractions and Hotels.
    
    ### Collection Details:
    1. **Attractions Collection**: Contains information about attractions and activities
    2. **Hotels Collection**: Contains information about hotels and accommodations
    
    ### Important Instructions:
    1. **Relationship between collections**: 
       - Attractions and Hotels collections both have unique `attraction_id` and `hotel_id` respectively along with `destination_id` (which should be used to filter attractions and hotels for a specific destination).
       - When a user asks about a specific destination, you should use the destination's `destination_id` to filter attractions and hotels
    2. **Response Requirements**:
       - For ANY destination-related query, ALWAYS include:
         - Personalized destination information based on the user query
         - At least 3 recommended attractions to visit (filtered by the destination_id)
         - At least 3 recommended hotels (filtered by the destination_id)
       - Response must be well structured and in a friendly tone.
       - Response must be easy to read and understand.
    """
    
    if destination_id and destination_name:
        specific_instructions = f"""
    ### Specific Destination Information That Should Be Used:
    - The user here is specifically asking about {destination_name}
    - The destination_id for {destination_name} is: '{destination_id}'
    - You should use this destination_id (TEXT) to filter attractions and hotels where destination_id matches the destination_id of the attraction or hotel
    Like this: Filter.by_property("destination_id").equal("{destination_id}")
    """
        return base_prompt + specific_instructions
    else:
        return base_prompt


def run_travel_query(client, user_query):
    destination_id, destination_name = find_destination_id(client, user_query)
    
    system_prompt = create_dynamic_system_prompt(destination_id, destination_name)
    
    travel_agent = QueryAgent(
        client=client,
        collections=["Attractions", "Hotels"],
        system_prompt=system_prompt,
    )
    
    response = travel_agent.run(user_query)
    
    return response


client = connect_to_weaviate()

user_query = "Plan a trip to Paris for 3 days, including the places to visit and the hotels to stay at"

response = run_travel_query(client, user_query)

print_query_agent_response(response)

# # Example of a follow-up query
# follow_up_query = "Nice, can you also suggest some family-friendly activities?"
# following_response = run_travel_query(client, follow_up_query)
# print_query_agent_response(following_response)

# Close the client connection
client.close()
