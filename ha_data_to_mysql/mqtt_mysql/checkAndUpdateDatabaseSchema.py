import mysql.connector
import os
import glob

MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'mqttdata'),
    'password': os.getenv('MYSQL_PWD', 'mqttdata'),
    'database': os.getenv('MYSQL_DATABASE', 'mqtt_data'),
    'port': int(os.getenv('MYSQL_PORT', 3306))
}


def getCurrentSchemaVersion():
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT version FROM schema_version WHERE validity = 1")
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return row['version'] if row else 1
    except Exception as e:
        print(f"Error reading schema version: {e}")
        return 1


def apply_migration(file_path):
    with open(file_path, 'r') as f:
        sql_commands = f.read().split(';')  # split on semicolons

    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor()
    for command in sql_commands:
        command = command.strip()
        if command:  # skip empty lines
            try:
                print(f"Executing: {command}")
                cursor.execute(command)
            except Exception as e:
                print(f"Failed to execute: {command} → {e}")
                conn.rollback()
                cursor.close()
                conn.close()
                raise e
    conn.commit()
    cursor.close()
    conn.close()


def check_and_update_schema():
    current_version = getCurrentSchemaVersion()
    print(f"Current DB schema version: {current_version}")

    #migration_files = sorted(glob.glob("migrations/*.sql"))
    migration_files = sorted(
    glob.glob("migrations/*.sql"),
    key=lambda x: int(os.path.splitext(os.path.basename(x))[0])
)
    for file in migration_files:
        version = int(os.path.splitext(os.path.basename(file))[0])
        if version > current_version:
            print(f"Applying migration {version} from {file}...")
            apply_migration(file)
            print(f"Migration {version} applied successfully!")


if __name__ == "__main__":
    check_and_update_schema()