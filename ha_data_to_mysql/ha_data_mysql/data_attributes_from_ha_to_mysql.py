import asyncio
import websockets
import json
import mysql.connector
import time
import os

# ------------------------
# Home Assistant Config
# ------------------------

HA_URL = os.getenv('HA_URL')
TOKEN = os.getenv('HA_TOKEN')

#HA_URL = "ws://192.168.2.68:8123/api/websocket"
#TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIxZjczZGI4MGYxYjI0NmQyYWNkNzFjNjdkZGU0N2IxOSIsImlhdCI6MTc1NDIxOTU4OCwiZXhwIjoyMDY5NTc5NTg4fQ.KN79YP0rqtPL9ZFeQxNLRJGCs-o3YE0obrssMyVB13k"

# ------------------------
# MySQL Config
# ------------------------
DB_CONFIG = {
    'host':  os.getenv('MYSQL_HOST', 'localhost'),
    'user':  os.getenv('MYSQL_USER', 'mqttdata'),
    'password': os.getenv('MYSQL_PWD', 'mqttdata'),
    'database': os.getenv('MYSQL_DATABASE', 'mqtt_data'),
    'port': os.getenv('MYSQL_PORT', 3306)
    }



def init_db():
    """Ensure the required tables exist."""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ha_state_change (
            changeid INT AUTO_INCREMENT PRIMARY KEY,
            entity VARCHAR(255) NOT NULL,
            friendly_name VARCHAR(255),
            state VARCHAR(255),
            ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ha_state_attributes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            changeid INT NOT NULL,
            attribute VARCHAR(255),
            value TEXT,
            FOREIGN KEY (changeid) REFERENCES ha_state_change(changeid) ON DELETE CASCADE
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Database initialized with required tables.")


# ------------------------
# DB Insert Function
# ------------------------
def insert_state_and_attributes(entity_id, friendly_name, state, attributes):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Insert into ha_state_change
        cursor.execute("""
            INSERT INTO ha_state_change (entity, friendly_name, state)
            VALUES (%s, %s, %s)
        """, (entity_id, friendly_name, state))
        change_id = cursor.lastrowid

        # Insert attributes into ha_state_attributes
        for key, value in attributes.items():
            cursor.execute("""
                INSERT INTO ha_state_attributes (changeid, attribute, value)
                VALUES (%s, %s, %s)
            """, (change_id, key, str(value)))

        conn.commit()
        cursor.close()
        conn.close()
        print(f"Inserted {entity_id} with {len(attributes)} attributes into DB.")

    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")

# ------------------------
# WebSocket Listener
# ------------------------
async def listen_to_ha():
    async with websockets.connect(HA_URL) as ws:
        # Step 1: Receive auth_required
        await ws.recv()

        # Step 2: Send auth
        await ws.send(json.dumps({
            "type": "auth",
            "access_token": TOKEN
        }))

        # Step 3: Wait for auth_ok
        await ws.recv()

        # Step 4: Subscribe to state changes
        await ws.send(json.dumps({
            "id": 1,
            "type": "subscribe_events",
            "event_type": "state_changed"
        }))

        print("Subscribed to state changes.")

        # Step 5: Handle incoming messages
        while True:
            msg = await ws.recv()
            data = json.loads(msg)

            event = data.get("event", {})
            event_data = event.get("data", {})
            entity_id = event_data.get("entity_id")
            new_state = event_data.get("new_state", {})

            state = new_state.get("state")
            attributes = new_state.get("attributes", {})
            friendly_name = attributes.get("friendly_name", f"Unknown, {entity_id}")

            if entity_id and state is not None:
                print(f"{entity_id}: {state}")
                for key, value in attributes.items():
                    print(f"  - {key}: {value}")
                print("---")

                # Save to DB
                insert_state_and_attributes(entity_id, friendly_name, state, attributes)

# ------------------------
# Run
# ------------------------
time.sleep(45)
init_db()
asyncio.run(listen_to_ha())
