import os
import time
import json
import random
import asyncio
from datetime import datetime, timezone
from dotenv import load_dotenv
from azure.eventhub.aio import EventHubProducerClient
from azure.eventhub import EventData

# Load environment variables from .env file
load_dotenv()

EVENT_HUB_CONNECTION_STR = os.getenv("EVENT_HUB_CONNECTION_STR")
EVENT_HUB_NAME = os.getenv("EVENT_HUB_NAME")

if not EVENT_HUB_CONNECTION_STR or not EVENT_HUB_NAME:
    raise ValueError("Missing EVENT_HUB_CONNECTION_STR or EVENT_HUB_NAME in .env file.")

SERVERS = ["app-vm-01", "app-vm-02", "db-vm-01", "gw-501", "gw-502"]
USERS = ["admin", "root", "shawn", "service_acct_01", "guest"]

IPS = [
    "192.168.1.50", "10.0.0.12", "172.16.254.1", 
    "203.0.113.4", # "External" suspicious IP
    "198.51.100.22"
]
EVENTS = [
    "HTTP 200 OK", "Database Connection Established", "User Logout",
    "Failed SSH login", "Failed SSH login", "Failed SSH login", # Weighted to happen more often
    "SQL Injection attempt detected", "High Memory Usage"
]

def generate_mock_log():
    event_type = random.choice(EVENTS)
    
    if "Failed" in event_type or "Injection" in event_type:
        severity = "CRITICAL" if "Injection" in event_type else "WARNING"
    elif "Memory" in event_type:
        severity = "WARNING"
    else:
        severity = "INFO"

    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "server": random.choice(SERVERS),
        "ip": random.choice(IPS),
        "user": random.choice(USERS),
        "event": event_type,
        "severity": severity,
        "process_id": random.randint(1000, 9999)
    }
    return log_entry

async def run_generator():
    print("Starting generator...")
    
    producer = EventHubProducerClient.from_connection_string(
        conn_str=EVENT_HUB_CONNECTION_STR,
        eventhub_name=EVENT_HUB_NAME
    )
    
    async with producer:
        try:
            while True:
                event_data_batch = await producer.create_batch()
                batch_size = random.randint(5, 20)
                
                for _ in range(batch_size):
                    log = generate_mock_log()
                    event_data = EventData(json.dumps(log).encode('utf-8'))
                    
                    try:
                        event_data_batch.add(event_data)
                    except ValueError:
                        await producer.send_batch(event_data_batch)
                        event_data_batch = await producer.create_batch()
                        event_data_batch.add(event_data)
                
                if len(event_data_batch) > 0:
                    await producer.send_batch(event_data_batch)
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Sent batch of {batch_size} logs.")
                
                await asyncio.sleep(random.uniform(1.0, 3.0))
                
        except KeyboardInterrupt:
            print("\nStopped.")
        except Exception as e:
            print(f"\nError: {e}")

if __name__ == "__main__":
    asyncio.run(run_generator())
