import requests
from bs4 import BeautifulSoup
import json
from kafka import KafkaProducer
import time
import os

# Detect whether running inside Docker or locally
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")  # Default to Docker network

# If running locally, override KAFKA_BROKER to localhost
if not os.getenv("RUNNING_IN_DOCKER"):
    KAFKA_BROKER = "localhost:9092"

TOPIC = "cricket_scores"

# Initialize Kafka producer
try:
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BROKER],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    print(f" Connected to Kafka at {KAFKA_BROKER}")
except Exception as e:
    print(" Failed to connect to Kafka:", e)
    exit(1)


# Function to scrape match results
def scrape_scores():
    url = "https://www.espncricinfo.com/live-cricket-match-results"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f" Failed to fetch page, status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")

    # Locate match result containers
    match_containers = soup.find_all("div", class_="ds-px-4 ds-py-3")

    if not match_containers:
        print("⚠️ No match data found.")
        return []

    scores = []
    for match in match_containers:
        try:
            teams = match.find_all("p", class_="ds-text-tight-m")
            result_tag = match.find("p", class_="ds-text-tight-s")  # Check if exists

            if len(teams) < 2:
                print("⚠️ Skipping match due to missing team names.")
                continue  # Skip incomplete match data

            team_1 = teams[0].text.strip()
            team_2 = teams[1].text.strip()

            # Handle missing result safely
            result = result_tag.text.strip() if result_tag else "Result not available"

            # ✅ **Transform Data Before Sending to Kafka**
            structured_data = {
                "team_1": team_1,
                "team_2": team_2,
                "match_result": result,
                "timestamp": time.time()  # Adding timestamp for tracking
            }

            scores.append(structured_data)  # Store structured data

        except Exception as e:
            print(f" Error parsing match: {e}")

    return scores


# Function to publish data to Kafka
def publish_to_kafka():
    while True:
        try:
            scores = scrape_scores()
            if scores:
                for record in scores:
                    try:
                        producer.send(TOPIC, record)  #  Send transformed data to Kafka
                    except Exception as kafka_error:
                        print(" Error sending to Kafka:", kafka_error)
                producer.flush()
                print(" Published to Kafka:", scores)
            else:
                print("No new match data found.")

        except Exception as e:
            print(" Error:", e)

        time.sleep(60)  # Scrape every 60 seconds


if __name__ == "__main__":
    publish_to_kafka()
