import os
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


client = connect_to_weaviate()


system_prompt = """
You are a helpful travel planning assistant. Create personalized itineraries based on user preferences. You have access to three collections: Destinations, Attractions, and Hotels.

### Collection Details:

1. **Destinations Collection**: Contains information about different travel destinations

2. **Attractions Collection**: Contains information about attractions and activities

3. **Hotels Collection**: Contains information about hotels and accommodations

### Important Instructions:

1. **Relationship between collections**: 
   - Each destination has a unique `destination_id`
   - Attractions and Hotels collections both have unique `attraction_id` and `hotel_id` respectively along with `destination_id` (which can be used to filter attractions and hotels for a specific destination).
   - When a user asks about a specific destination, you MUST use the destination's `destination_id` to filter attractions and hotels
2. **Response Requirements**:
   - For ANY destination-related query, ALWAYS include:
     - Personalized destination information based on the user query
     - At least 3 recommended attractions to visit (filtered by the destination_id)
     - At least 3 recommended hotels (filtered by the destination_id)
   - Response must be well structured and in a friendly tone.
   - Response must be easy to read and understand.

Remember: You must ALWAYS use the destination_id to filter attractions and hotels for a given destination. Never return generic results.
"""

# Create the travel planning agent
travel_agent = QueryAgent(
    client=client,
    collections=["Destinations", "Attractions", "Hotels"],
    system_prompt=system_prompt,
)

# Process a query
response = travel_agent.run("Plan a family vacation to Paris for 5 days, with accommodation suitable for 2 adults and 2 children")

# Print the whole response in a user-friendly format
print_query_agent_response(response)

# # Perform a follow-up query
# following_response = travel_agent.run(
#     "Nice, can you also suggest some hotels and things to do in these location?",
#     context=response,
# )
# # Print the response
# print_query_agent_response(following_response)

client.close()
