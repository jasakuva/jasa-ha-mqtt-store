import json
import mysql.connector
import os
import time

# Constants for retry behavior
MAX_RETRIES = 20
WAIT_SECONDS = 2


def createDatabase():
    config = {
        'host':  os.getenv('MYSQL_HOST', 'localhost'),
        'user':  os.getenv('MYSQL_USER', 'mqttdata'),
        'password': os.getenv('MYSQL_PWD', 'mqttdata'),
        'database': os.getenv('MYSQL_DATABASE', 'mqtt_data'),
        'port': os.getenv('MYSQL_PORT', 3306)
    }

    conn = None
    cursor = None

    for attempt in range(MAX_RETRIES):
        try:
            print(f"Attempt {attempt + 1} of {MAX_RETRIES} to connect to MySQL...")
            conn = mysql.connector.connect(**config)
            if conn.is_connected():
                print("Connected to MySQL database")
                cursor = conn.cursor(dictionary=True)

                # Table creation queries
                queries = [
                    """CREATE TABLE IF NOT EXISTS `message_json` (
                        `messageid` int NOT NULL AUTO_INCREMENT,
                        `sourceid` int DEFAULT NULL,
                        `message` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
                        `topic` varchar(255) NOT NULL,
                        `creationtime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (`messageid`),
                        UNIQUE KEY `messageid` (`messageid`),
                        KEY `sourceid` (`sourceid`)
                        ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci""",
                    """CREATE TABLE IF NOT EXISTS `message_variabledata` (
                        `messageid` int NOT NULL,
                        `variable` varchar(255) NOT NULL,
                        `data` varchar(255) NOT NULL
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci""",
                    """CREATE TABLE IF NOT EXISTS `sources` (
                        `sourceid` int NOT NULL AUTO_INCREMENT,
                        `name` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
                        `source_mqtt_key` varchar(255) NOT NULL,
                        PRIMARY KEY (`sourceid`),
                        KEY `sourceid` (`sourceid`)
                        ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci"""
                ]

                for query in queries:
                    cursor.execute(query)

                conn.commit()
                print("Tables created successfully")
                break  # Exit loop if successful

        except mysql.connector.Error as err:
            print(f"MySQL connection failed (attempt {attempt + 1}/{MAX_RETRIES}): {err}")
            if attempt < MAX_RETRIES - 1:
                print(f"Retrying in {WAIT_SECONDS} seconds...")
                time.sleep(WAIT_SECONDS)

        finally:
            if cursor is not None:
                cursor.close()
                cursor = None
            if conn is not None and conn.is_connected():
                conn.close()
                conn = None
    else:
        print("Could not connect to MySQL after maximum retries.")