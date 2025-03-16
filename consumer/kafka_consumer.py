from kafka import KafkaConsumer
import json
import os
import mysql.connector
from mysql.connector.constants import ClientFlag

# Kafka and MySQL configurations
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")

# MySQL Connection Setup with explicit client flags to skip charset
try:
    db = mysql.connector.connect(
        host=MYSQL_HOST,
        user="root",
        password="root",
        database="cricket_db",
        client_flags=[ClientFlag.IGNORE_SPACE, ClientFlag.LOCAL_FILES],
        use_pure=True,  # Use pure Python implementation
        charset="utf8"  # Try to disable charset handling
    )
    print("✅ Connected to MySQL database")
    cursor = db.cursor()
except Exception as e:
    print(f"❌ Error connecting to MySQL: {e}")
    raise e

# Kafka Consumer Setup
try:
    consumer = KafkaConsumer(
        'cricket_scores',
        bootstrap_servers=[KAFKA_BROKER],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='cricket-group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    print(f"✅ Connected to Kafka at {KAFKA_BROKER}, listening for messages...\n")
except Exception as e:
    print(f"❌ Error connecting to Kafka: {e}")
    raise e

# Process Incoming Messages
try:
    for message in consumer:
        data = message.value  # Deserialize JSON

        print(f"📩 Received message: {data}")  # Print received message for debugging

        try:
            # Extract structured fields
            team_1 = data.get("team_1", "Unknown")
            team_2 = data.get("team_2", "Unknown")
            match_result = data.get("match_result", "Result unavailable")
            timestamp = data.get("timestamp", 0)

            # Insert into MySQL
            sql = "INSERT INTO cricket_scores (team_1, team_2, match_result, timestamp) VALUES (%s, %s, %s, %s)"
            values = (team_1, team_2, match_result, timestamp)
            cursor.execute(sql, values)
            db.commit()

            print(f"✅ Stored in MySQL: {data}\n")

        except Exception as e:
            print(f"❌ Error processing message: {e}")
except KeyboardInterrupt:
    print("Consumer stopped by user")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
finally:
    # Close the database connection
    if 'cursor' in locals() and cursor:
        cursor.close()
    if 'db' in locals() and db:
        db.close()