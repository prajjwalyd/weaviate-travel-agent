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

# Create the travel planning agent
travel_agent = QueryAgent(
    client=client,
    collections=["Destinations", "Attractions"],
    system_prompt="You are a helpful travel planning assistant. Create personalized itineraries based on user preferences. You have access to two collections: Destinations and Attractions. Each destination object has `destination_id` which is unique to it and is used to link to its attractions in the Attractions collection. Each attraction object has `attraction_id` which is unique to it. You may have to translate the user query to perform searches. But you must always respond to the user in their own language.",
)

# Process a query
response = travel_agent.run("Compare London and Paris for a 3-day vacation")

# Print the whole response in a user-friendly format
print_query_agent_response(response)

client.close()
