from kafka import KafkaConsumer
import json
import os
import mysql.connector

# Kafka and MySQL configurations
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")

# MySQL Connection Setup
db = mysql.connector.connect(
    host=MYSQL_HOST,
    user="root",
    password="root",
    database="cricket_db"
)
cursor = db.cursor()

# Kafka Consumer Setup
consumer = KafkaConsumer(
    'cricket_scores',
    bootstrap_servers=[KAFKA_BROKER],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='cricket-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print(f"✅ Connected to Kafka at {KAFKA_BROKER}, listening for messages...\n")

# Process Incoming Messages
for message in consumer:
    data = message.value  # Deserialize JSON

    print(f"📩 Received message: {data}")  # ✅ Print received message for debugging

    try:
        # Extract structured fields
        team_1 = data.get("team_1", "Unknown")
        team_2 = data.get("team_2", "Unknown")
        match_result = data.get("match_result", "Result unavailable")
        timestamp = data.get("timestamp", 0)
        print(f"Received message: {data}")  # Debugging line before MySQL insertion
        # Insert into MySQL
        sql = "INSERT INTO cricket_scores (team_1, team_2, match_result, timestamp) VALUES (%s, %s, %s, %s)"
        values = (team_1, team_2, match_result, timestamp)
        cursor.execute(sql, values)
        db.commit()

        print(f" Stored in MySQL: {data}\n")  #  Confirm data is stored

    except Exception as e:
        print(f" Error processing message: {e}")  # Debugging error handling

# Close the database connection (this won't execute unless the script is stopped)
cursor.close()
db.close()
