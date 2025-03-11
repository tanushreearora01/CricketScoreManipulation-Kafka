from kafka import KafkaConsumer
import json

# Kafka Consumer setup
consumer = KafkaConsumer(
    'cricket_scores',  # Make sure the topic name matches
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='cricket-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))  # Auto deserialize JSON
)

print("Listening for messages...")

for message in consumer:
    data = message.value  # Directly gets the JSON object
    print(f"Received Data: {data}")  # Debugging: Print raw data

    # Process data properly
    try:
        processed_data = {
            "teams": data["teams"],
            "result": data["result"],
            "timestamp": data["timestamp"]
        }
        print(f"Processed Data: {processed_data}")

    except KeyError as e:
        print(f"Missing expected field: {e}")
