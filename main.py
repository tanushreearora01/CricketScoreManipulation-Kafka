import requests
from bs4 import BeautifulSoup
import json
from kafka import KafkaProducer
import time

# ✅ Kafka configuration
KAFKA_BROKER = "localhost:9092"
TOPIC = "cricket_scores"

# ✅ Initialize Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BROKER],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# ✅ Function to scrape cricket scores from the statistics page
def scrape_scores():
    url = "https://www.espncricinfo.com/stats"  # Replace with the actual URL from your screenshot
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Locate the table containing match results
    table = soup.find("table")  # Adjust selector if needed
    rows = table.find_all("tr")[1:]  # Skip header row

    scores = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 4:
            continue  # Skip invalid rows

        date = cols[0].text.strip()
        teams = cols[1].text.strip()
        venue = cols[2].text.strip()
        result = cols[3].text.strip()
        scorecard_link = cols[4].find("a")["href"] if cols[4].find("a") else "N/A"

        scores.append({
            "date": date,
            "teams": teams,
            "venue": venue,
            "result": result,
            "scorecard": scorecard_link,
            "timestamp": time.time()
        })

    return scores

# ✅ Function to publish data to Kafka
def publish_to_kafka():
    while True:
        try:
            scores = scrape_scores()
            if scores:
                for record in scores:
                    producer.send(TOPIC, record)
                producer.flush()
                print("Published to Kafka:", scores)
            else:
                print("No match data found.")
        except Exception as e:
            print("Error:", e)

        time.sleep(60)  # Adjust frequency of scraping

if __name__ == "__main__":
    publish_to_kafka()