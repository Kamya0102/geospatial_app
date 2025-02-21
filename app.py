from flask import Flask, jsonify, render_template
from azure.cosmos import CosmosClient, exceptions

app = Flask(__name__)

# 1️⃣ **Azure Cosmos DB Connection Details**
COSMOS_DB_URI = "https://acregistry123.documents.azure.com:443/"
COSMOS_DB_KEY = "5gxQ7Kx9DzZQy1uDjTxrMdmASuLpxDLdfRviWSHqpXdX1DpJ7DO0syhLxLqVT1Xa1SCFZbJBtKECACDbrNlvqg=="
DATABASE_NAME = "cb_geom_2states"
CONTAINER_NAME = "geospatial"
PARTITION_KEY = "/geoid"

# 2️⃣ **Connect to CosmosDB**
client = CosmosClient(COSMOS_DB_URI, credential=COSMOS_DB_KEY)
database = client.get_database_client(DATABASE_NAME)
container = database.get_container_client(CONTAINER_NAME)

@app.route('/')
def home():
    """Render the HTML page with the map."""
    return render_template('map.html')  # Ensure 'map.html' exists in the templates folder

@app.route('/data', methods=['GET'])
def fetch_data():
    """Fetch geospatial data from CosmosDB and return as GeoJSON."""
    try:
        print("Fetching data from CosmosDB...")  # Debug log
        query = "SELECT * FROM c"
        items = list(container.query_items(query, enable_cross_partition_query=True))
        print(f"Retrieved {len(items)} items from CosmosDB.")  # Debug log

        # Convert CosmosDB records to GeoJSON format
        geojson = {
            "type": "FeatureCollection",
            "features": []
        }

        for item in items:
            if 'geometry' in item:  # Ensure the record has geometry data
                feature = {
                    "type": "Feature",
                    "geometry": item["geometry"],  # CosmosDB should have 'geometry' field
                    "properties": {
                        "id": item["id"],
                        "geoid": item.get("geoid", "N/A"),
                        "name": item.get("name", "Unnamed")  # Add more properties if needed
                    }
                }
                geojson["features"].append(feature)

        return jsonify(geojson)

    except exceptions.CosmosHttpResponseError as e:
        print(f"Error fetching data: {e}")  # Debug log
        return jsonify({"error": str(e)}), 500

@app.route('/count', methods=['GET'])
def count_documents():
    """Count the total number of documents in the CosmosDB container."""
    try:
        print("Counting documents in CosmosDB...")  # Debug log
        query = "SELECT VALUE COUNT(1) FROM c"
        results = list(container.query_items(query, enable_cross_partition_query=True))
        count = results[0] if results else 0
        print(f"Total documents: {count}")  # Debug log
        return jsonify({"total_documents": count})

    except exceptions.CosmosHttpResponseError as e:
        print(f"Error counting documents: {e}")  # Debug log
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting Flask app...")  # Debug log
    app.run(debug=True)
