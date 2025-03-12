from kafka import KafkaConsumer
import json
import mysql.connector

# MySQL Connection Setup
db = mysql.connector.connect(
    host="localhost",   # If using Docker, replace with MySQL container name (e.g., "mysql-db")
    user="root",
    password="root",
    database="cricket_db"
)
cursor = db.cursor()

#  Kafka Consumer Setup
consumer = KafkaConsumer(
    'cricket_scores',  # Ensure this matches the producer topic
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='cricket-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))  # Deserialize JSON
)

print("Listening for transformed messages...")

# Process Incoming Messages from Kafka
for message in consumer:
    data = message.value  #  Already structured JSON

    try:
        #  Extract structured fields
        team_1 = data["team_1"]
        team_2 = data["team_2"]
        match_result = data["match_result"]
        timestamp = data["timestamp"]

        #  Insert into MySQL
        sql = "INSERT INTO cricket_scores (team_1, team_2, match_result, timestamp) VALUES (%s, %s, %s, %s)"
        values = (team_1, team_2, match_result, timestamp)
        cursor.execute(sql, values)
        db.commit()

        print(f" Stored in MySQL: {data}")

    except KeyError as e:
        print(f" Missing field: {e}")  # Debugging error handling

# Close the database connection (this won't execute unless the script is stopped)
cursor.close()
db.close()
