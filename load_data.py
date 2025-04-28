import os
import json
import weaviate
from weaviate.auth import Auth
from weaviate.classes.config import Configure, Property, DataType
from weaviate.agents.query import QueryAgent
from dotenv import load_dotenv

load_dotenv()

headers = {
    "X-OpenAI-Api-Key": os.environ["OPENAI_API_KEY"],
}


def create_uuid_from_destination_id(destination_id):
    from weaviate.util import generate_uuid5

    # Generate a deterministic UUID based on the destination_id
    # This ensures the same destination_id always generates the same UUID
    uuid = generate_uuid5(destination_id)
    print(f"Generated UUID for destination ID: {destination_id} is {uuid}")
    return uuid


def create_uuid_from_attraction_id(attraction_id):
    from weaviate.util import generate_uuid5

    # Generate a deterministic UUID based on the attraction_id
    # This ensures the same attraction_id always generates the same UUID
    uuid = generate_uuid5(attraction_id)
    print(f"Generated UUID for attraction ID: {attraction_id} is {uuid}")
    return uuid


def create_uuid_from_hotel_id(hotel_id):
    from weaviate.util import generate_uuid5

    # Generate a deterministic UUID based on the hotel_id
    # This ensures the same hotel_id always generates the same UUID
    uuid = generate_uuid5(hotel_id)
    print(f"Generated UUID for hotel ID: {hotel_id} is {uuid}")
    return uuid


try:
    # Connect to Weaviate
    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=os.environ["WEAVIATE_URL"],
        auth_credentials=Auth.api_key(os.environ["WEAVIATE_API_KEY"]),
        headers=headers,
    )

    if client.is_ready():
        print("Weaviate is ready!")
    else:
        print("Weaviate is not ready.")

    if not client.collections.exists("Destinations"):
        client.collections.create(
            "Destinations",
            description="A collection of travel destinations with their details",
            vectorizer_config=Configure.Vectorizer.text2vec_openai(),
            properties=[
                Property(
                    name="destination_id",
                    data_type=DataType.TEXT,
                    description="The unique identifier of the destination",
                    skip_vectorization=True,
                ),
                Property(
                    name="name",
                    data_type=DataType.TEXT,
                    description="The name of the destination",
                ),
                Property(
                    name="description",
                    data_type=DataType.TEXT,
                    description="A detailed description of the destination",
                ),
                Property(
                    name="climate",
                    data_type=DataType.TEXT,
                    description="The climate of the destination",
                ),
                Property(
                    name="avg_monthly_temp",
                    data_type=DataType.OBJECT_ARRAY,
                    skip_vectorization=True,
                    description="Average monthly temperature in Celsius",
                    nested_properties=[
                        Property(
                            name="month",
                            data_type=DataType.INT,
                            skip_vectorization=True,
                        ),
                        Property(
                            name="temp", data_type=DataType.INT, skip_vectorization=True
                        ),
                    ],
                ),
                Property(
                    name="best_time_to_visit",
                    data_type=DataType.TEXT,
                    description="The best time of year to visit the destination",
                ),
                Property(
                    name="avg_daily_cost_range",
                    data_type=DataType.NUMBER_ARRAY,
                    skip_vectorization=True,
                    description="Average daily cost range in USD",
                ),
                Property(
                    name="tags",
                    data_type=DataType.TEXT_ARRAY,
                    description="Tags associated with the destination",
                ),
                Property(
                    name="image",
                    data_type=DataType.TEXT,
                    skip_vectorization=True,
                    description="URL of the destination image",
                ),
            ],
        )
        print("Destinations collection created.")
        # Load data
        with open("dataset/destinations.json", "r", encoding="utf-8") as f:
            destinations_data = json.load(f)
            destinations_collection = client.collections.get("Destinations")
            with destinations_collection.batch.dynamic() as batch:
                for item in destinations_data:
                    uuid = create_uuid_from_destination_id(item["id"])
                    # Add the item with the generated UUID
                    batch.add_object(
                        properties={
                            "destination_id": item["id"],
                            "name": item["name"],
                            "description": item["description"],
                            "climate": item["climate"],
                            "avg_monthly_temp": item["avg_monthly_temp"],
                            "best_time_to_visit": item["best_time_to_visit"],
                            "avg_daily_cost_range": item["avg_daily_cost_range"],
                            "tags": item["tags"],
                            "image": item["image"],
                        },
                        uuid=uuid,
                    )
                    print(f"Added destination: {item['name']} with UUID: {uuid}")
    else:
        print("Destinations collection already exists.")

    if not client.collections.exists("Attractions"):
        client.collections.create(
            "Attractions",
            description="A collection of attractions and activities at different destinations",
            vectorizer_config=Configure.Vectorizer.text2vec_openai(),
            properties=[
                Property(
                    name="attraction_id",
                    data_type=DataType.TEXT,
                    description="The unique identifier of the attraction",
                    skip_vectorization=True,
                ),
                # Implement karna hai
                Property(
                    name="destination_id",
                    data_type=DataType.TEXT,
                    description="The unique identifier of the destination",
                    skip_vectorization=True,
                ),
                Property(
                    name="name",
                    data_type=DataType.TEXT,
                    description="The name of the attraction",
                ),
                Property(
                    name="subcategories",
                    data_type=DataType.TEXT_ARRAY,
                    description="Subcategories of the attraction",
                ),
                Property(
                    name="locationString",
                    data_type=DataType.TEXT,
                    description="The location of the attraction as a string",
                ),
                Property(
                    name="description",
                    data_type=DataType.TEXT,
                    description="A detailed description of the attraction",
                ),
                Property(
                    name="image",
                    data_type=DataType.TEXT,
                    skip_vectorization=True,
                    description="URL of the attraction's main image",
                ),
                Property(
                    name="rankingPosition",
                    data_type=DataType.INT,
                    skip_vectorization=True,
                    description="Ranking position of the attraction",
                ),
                Property(
                    name="rating",
                    data_type=DataType.NUMBER,
                    skip_vectorization=True,
                    description="Average rating of the attraction",
                ),
                Property(
                    name="addressObj",
                    data_type=DataType.OBJECT,
                    skip_vectorization=True,
                    description="Structured address object of the attraction",
                    nested_properties=[
                        Property(
                            name="street1",
                            data_type=DataType.TEXT,
                            skip_vectorization=True,
                        ),
                        Property(
                            name="street2",
                            data_type=DataType.TEXT,
                            skip_vectorization=True,
                        ),
                        Property(
                            name="city",
                            data_type=DataType.TEXT,
                            skip_vectorization=True,
                        ),
                        Property(
                            name="state",
                            data_type=DataType.TEXT,
                            skip_vectorization=True,
                        ),
                        Property(
                            name="country",
                            data_type=DataType.TEXT,
                            skip_vectorization=True,
                        ),
                        Property(
                            name="postalcode",
                            data_type=DataType.TEXT,
                            skip_vectorization=True,
                        ),
                    ],
                ),
                Property(
                    name="email",
                    data_type=DataType.TEXT,
                    skip_vectorization=True,
                    description="Contact email of the attraction",
                ),
                Property(
                    name="latitude",
                    data_type=DataType.NUMBER,
                    skip_vectorization=True,
                    description="Latitude coordinate of the attraction",
                ),
                Property(
                    name="longitude",
                    data_type=DataType.NUMBER,
                    skip_vectorization=True,
                    description="Longitude coordinate of the attraction",
                ),
                Property(
                    name="webUrl",
                    data_type=DataType.TEXT,
                    skip_vectorization=True,
                    description="TripAdvisor web URL for the attraction",
                ),
                Property(
                    name="website",
                    data_type=DataType.TEXT,
                    skip_vectorization=True,
                    description="Official website of the attraction",
                ),
                Property(
                    name="rankingString",
                    data_type=DataType.TEXT,
                    description="Ranking description of the attraction",
                ),
                Property(
                    name="ratingHistogram",
                    data_type=DataType.OBJECT,
                    skip_vectorization=True,
                    description="Distribution of ratings",
                    nested_properties=[
                        Property(
                            name="count1",
                            data_type=DataType.INT,
                            skip_vectorization=True,
                        ),
                        Property(
                            name="count2",
                            data_type=DataType.INT,
                            skip_vectorization=True,
                        ),
                        Property(
                            name="count3",
                            data_type=DataType.INT,
                            skip_vectorization=True,
                        ),
                        Property(
                            name="count4",
                            data_type=DataType.INT,
                            skip_vectorization=True,
                        ),
                        Property(
                            name="count5",
                            data_type=DataType.INT,
                            skip_vectorization=True,
                        ),
                    ],
                ),
                Property(
                    name="numberOfReviews",
                    data_type=DataType.INT,
                    skip_vectorization=True,
                    description="Total number of reviews",
                ),
                Property(
                    name="subtype",
                    data_type=DataType.TEXT_ARRAY,
                    description="Subtypes of the attraction",
                ),
            ],
        )
        print("Attractions collection created.")
        # Load data
        with open("dataset/attractions.json", "r", encoding="utf-8") as f:
            attractions_data = json.load(f)
            attractions_collection = client.collections.get("Attractions")
            with attractions_collection.batch.dynamic() as batch:
                for item in attractions_data:
                    uuid = create_uuid_from_attraction_id(item["id"])
                    destination_id = item["ancestorLocations"][0]["id"]
                    # Add the item with the generated UUID
                    batch.add_object(
                        properties={
                            "attraction_id": item["id"],
                            "destination_id": destination_id,
                            "name": item.get("name"),
                            "subcategories": item.get("subcategories", []),
                            "locationString": item.get("locationString"),
                            "description": item.get("description"),
                            "image": item.get("image"),
                            "rankingPosition": item.get("rankingPosition"),
                            "rating": item.get("rating"),
                            "addressObj": item.get("addressObj"),
                            "email": item.get("email"),
                            "latitude": item.get("latitude"),
                            "longitude": item.get("longitude"),
                            "webUrl": item.get("webUrl"),
                            "website": item.get("website"),
                            "rankingString": item.get("rankingString"),
                            "ratingHistogram": item.get("ratingHistogram"),
                            "numberOfReviews": item.get("numberOfReviews"),
                            "subtype": item.get("subtype", []),
                        },
                        uuid=uuid,
                    )
                    print(f"Added attraction: {item['name']} with UUID: {uuid}")
    else:
        print("Attractions collection already exists.")

    if not client.collections.exists("Hotels"):
        client.collections.create(
            "Hotels",
            description="Collection of hotels in various destinations",
            vectorizer_config=Configure.Vectorizer.text2vec_openai(),
            properties=[
                Property(
                    name="hotel_id",
                    data_type=DataType.TEXT,
                    skip_vectorization=True,
                    description="The unique identifier of the hotel",
                ),
                Property(
                    name="destination_id",
                    data_type=DataType.TEXT,
                    skip_vectorization=True,
                    description="The unique identifier of the destination",
                ),
                Property(
                    name="name",
                    data_type=DataType.TEXT,
                    description="The name of the hotel",
                ),
                Property(
                    name="description",
                    data_type=DataType.TEXT,
                    description="The description of the hotel",
                ),
                Property(
                    name="image",
                    data_type=DataType.TEXT,
                    skip_vectorization=True,
                    description="URL of the hotel's main image",
                ),
                Property(
                    name="locationString",
                    data_type=DataType.TEXT,
                    description="Location string of the hotel",
                ),
                Property(
                    name="rankingPosition",
                    data_type=DataType.INT,
                    skip_vectorization=True,
                    description="Ranking position of the hotel",
                ),
                Property(
                    name="rating",
                    data_type=DataType.NUMBER,
                    skip_vectorization=True,
                    description="Average rating of the hotel",
                ),
                Property(
                    name="addressObj",
                    data_type=DataType.OBJECT,
                    skip_vectorization=True,
                    description="Structured address object of the hotel",
                    nested_properties=[
                        Property(
                            name="street1",
                            data_type=DataType.TEXT,
                            skip_vectorization=True,
                        ),
                        Property(
                            name="street2",
                            data_type=DataType.TEXT,
                            skip_vectorization=True,
                        ),
                        Property(
                            name="city",
                            data_type=DataType.TEXT,
                            skip_vectorization=True,
                        ),
                        Property(
                            name="state",
                            data_type=DataType.TEXT,
                            skip_vectorization=True,
                        ),
                        Property(
                            name="country",
                            data_type=DataType.TEXT,
                            skip_vectorization=True,
                        ),
                        Property(
                            name="postalcode",
                            data_type=DataType.TEXT,
                            skip_vectorization=True,
                        ),
                    ],
                ),
                Property(
                    name="email",
                    data_type=DataType.TEXT,
                    skip_vectorization=True,
                    description="Contact email of the hotel",
                ),
                Property(
                    name="latitude",
                    data_type=DataType.NUMBER,
                    skip_vectorization=True,
                    description="Latitude coordinate of the hotel",
                ),
                Property(
                    name="longitude",
                    data_type=DataType.NUMBER,
                    skip_vectorization=True,
                    description="Longitude coordinate of the hotel",
                ),
                Property(
                    name="webUrl",
                    data_type=DataType.TEXT,
                    skip_vectorization=True,
                    description="TripAdvisor web URL for the hotel",
                ),
                Property(
                    name="website",
                    data_type=DataType.TEXT,
                    skip_vectorization=True,
                    description="Official website of the hotel",
                ),
                Property(
                    name="rankingString",
                    data_type=DataType.TEXT,
                    description="Ranking description of the hotel",
                ),
                Property(
                    name="ratingHistogram",
                    data_type=DataType.OBJECT,
                    skip_vectorization=True,
                    description="Distribution of ratings",
                    nested_properties=[
                        Property(
                            name="count1",
                            data_type=DataType.INT,
                            skip_vectorization=True,
                        ),
                        Property(
                            name="count2",
                            data_type=DataType.INT,
                            skip_vectorization=True,
                        ),
                        Property(
                            name="count3",
                            data_type=DataType.INT,
                            skip_vectorization=True,
                        ),
                        Property(
                            name="count4",
                            data_type=DataType.INT,
                            skip_vectorization=True,
                        ),
                        Property(
                            name="count5",
                            data_type=DataType.INT,
                            skip_vectorization=True,
                        ),
                    ],
                ),
                Property(
                    name="numberOfReviews",
                    data_type=DataType.INT,
                    skip_vectorization=True,
                    description="Total number of reviews",
                ),
                Property(
                    name="hotelClass",
                    data_type=DataType.TEXT,
                    skip_vectorization=True,
                    description="Hotel class rating",
                ),
                Property(
                    name="amenities",
                    data_type=DataType.TEXT_ARRAY,
                    description="Amenities of the hotel",
                ),
                Property(
                    name="priceRange",
                    data_type=DataType.TEXT,
                    skip_vectorization=True,
                    description="Price range of the hotel",
                ),
                Property(
                    name="roomTips",
                    data_type=DataType.OBJECT_ARRAY,
                    description="Room tips of the hotel",
                    nested_properties=[
                        Property(
                            name="text",
                            data_type=DataType.TEXT,
                        ),
                        Property(
                            name="rating",
                            data_type=DataType.TEXT,
                            skip_vectorization=True,
                        ),
                    ],
                ),
                Property(
                    name="categoryReviewScores",
                    data_type=DataType.OBJECT_ARRAY,
                    description="Category review scores of the hotel",
                    nested_properties=[
                        Property(
                            name="categoryName",
                            data_type=DataType.TEXT,
                            skip_vectorization=True,
                        ),
                        Property(
                            name="score",
                            data_type=DataType.NUMBER,
                            skip_vectorization=True,
                        ),
                    ],
                ),
                Property(
                    name="aiReviewsSummary",
                    data_type=DataType.TEXT,
                    description="AI-generated summary of reviews for the hotel",
                ),
                Property(
                    name="photos",
                    data_type=DataType.TEXT_ARRAY,
                    skip_vectorization=True,
                    description="Photos of the hotel",
                ),
            ],
        )
        print("Hotels collection created.")
        # Load data
        with open("dataset/hotels.json", "r", encoding="utf-8") as f:
            hotels_data = json.load(f)
            hotels_collection = client.collections.get("Hotels")
            with hotels_collection.batch.dynamic() as batch:
                for item in hotels_data:
                    uuid = create_uuid_from_hotel_id(item["id"])
                    destination_id = item["ancestorLocations"][0]["id"]
                    # Add the item with the generated UUID
                    batch.add_object(
                        properties={
                            "hotel_id": item["id"],
                            "destination_id": destination_id,
                            "name": item.get("name"),
                            "description": item.get("description"),
                            "image": item.get("image"),
                            "locationString": item.get("locationString"),
                            "rankingPosition": item.get("rankingPosition"),
                            "rating": item.get("rating"),
                            "addressObj": item.get("addressObj"),
                            "email": item.get("email"),
                            "latitude": item.get("latitude"),
                            "longitude": item.get("longitude"),
                            "webUrl": item.get("webUrl"),
                            "website": item.get("website"),
                            "rankingString": item.get("rankingString"),
                            "ratingHistogram": item.get("ratingHistogram"),
                            "numberOfReviews": item.get("numberOfReviews"),
                            "hotelClass": item.get("hotelClass"),
                            "amenities": item.get("amenities"),
                            "priceRange": item.get("priceRange"),
                            "roomTips": (
                                [
                                    {
                                        "text": tip.get("text"),
                                        "rating": tip.get("rating"),
                                    }
                                    for tip in (item.get("roomTips") or [])
                                ]
                                if item.get("roomTips")
                                else None
                            ),
                            "categoryReviewScores": item.get("categoryReviewScores"),
                            "aiReviewsSummary": item.get("aiReviewsSummary"),
                            "photos": item.get("photos"),
                        },
                        uuid=uuid,
                    )
                    print(f"Added hotel: {item['name']} with UUID: {uuid}")
    else:
        print("Hotels collection already exists.")


except Exception as e:
    print(f"Error: {e}")
finally:
    client.close()
