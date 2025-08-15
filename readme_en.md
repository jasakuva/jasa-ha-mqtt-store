# Project Name

**Short Description:** This Python project collects Home Assistant entity states as they change and listens to MQTT queue messages, storing both types of data into a MySQL database.

---

## Features

- Collects Home Assistant entity values immediately when they change.
- Listens to MQTT topics and processes incoming messages.
- Stores both entity and MQTT data in a MySQL database.
- Runs entirely in Docker Compose with all services containerized.

---

## Architecture

The project runs in four Docker containers (via Docker Compose):

1. **MySQL** — the database where data is stored.
2. **phpMyAdmin** — web interface for managing the database.
3. **MQTT Loader** — Python service that listens to the MQTT broker and stores messages in the database.
4. **Home Assistant Loader** — Python service that listens to Home Assistant WebSocket API and stores entity values when they change.

---

## Installation and Startup (Docker Compose)

This project is designed to run with Docker Compose. Example `docker-compose.yml`:

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    logging:
      driver: "json-file"
      options:
        max-size: "50m"
        max-file: "3"
    container_name: jasa-ha-store-mysql
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: mqtt_data
      MYSQL_USER: mqttdata
      MYSQL_PASSWORD: mqttdata
      TZ: Europe/Helsinki
    command: --default-time-zone='Europe/Helsinki'
    ports:
      - "3606:3306"
    volumes:
      - jasa-ha-store:/var/lib/mysql

  phpmyadmin:
    image: phpmyadmin/phpmyadmin
    logging:
      driver: "json-file"
      options:
        max-size: "50m"
        max-file: "3"
    container_name: jasa-ha-store-phpmyadmin
    restart: always
    environment:
      PMA_HOST: mysql
      PMA_PORT: 3306
      PMA_USER: root
      PMA_PASSWORD: rootpassword
    ports:
      - "8480:80"
    depends_on:
      - mysql

  mqtt_loader:
    image: jasatest/jasa-mqtt-to-mysql
    logging:
      driver: "json-file"
      options:
        max-size: "50m"
        max-file: "3"
    container_name: jasa-ha-store-mqtt
    restart: always
    network_mode: host
    environment:
      MYSQL_PORT: 3606
    depends_on:
      - mysql

  ha_loader:
    image: jasatest/jasa-ha-to-mysql
    logging:
      driver: "json-file"
      options:
        max-size: "50m"
        max-file: "3"
    container_name: jasa-ha-store-ha
    restart: always
    network_mode: host
    environment:
      MYSQL_PORT: 3606
      HA_URL: ws://YOUR_HA_ADDRESS:8123/api/websocket
      HA_TOKEN: YOUR_HA_TOKEN
    depends_on:
      - mysql

volumes:
  jasa-ha-store:
```

**Start services:**

```bash
docker-compose up -d
```

---

## Configuration Parameters

**MySQL**

```
PMA_HOST=mysql
PMA_PORT=3306
PMA_USER=root
PMA_PASSWORD=rootpassword
```

**phpMyAdmin**

```
MYSQL_PORT=3606
```

**MQTT Loader**

```
MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_TOPIC=#
MYSQL_HOST=localhost
MYSQL_USER=mqttdata
MYSQL_PWD=mqttdata
MYSQL_DATABASE=mqtt_data
MYSQL_PORT=3306
```

**HA Loader**

```
MYSQL_HOST=localhost
MYSQL_USER=mqttdata
MYSQL_PWD=mqttdata
MYSQL_DATABASE=mqtt_data
MYSQL_PORT=3306
HA_URL=ws://my_ha_address:8123/api/websocket
HA_TOKEN=mytoken
```

---

## Database Tables and Columns

- **ha\_state\_change**

  - `changeid` (INT, PRIMARY KEY, AUTO\_INCREMENT)
  - `entity` (VARCHAR(255), NOT NULL)
  - `friendly_name` (VARCHAR(255))
  - `state` (VARCHAR(255))
  - `ts` (TIMESTAMP, DEFAULT CURRENT\_TIMESTAMP)

- **ha\_state\_attributes**

  - `id` (INT, PRIMARY KEY, AUTO\_INCREMENT)
  - `changeid` (INT, FOREIGN KEY → ha\_state\_change.changeid)
  - `attribute` (VARCHAR(255))
  - `value` (TEXT)

- **message\_json**

  - `messageid` (INT, PRIMARY KEY, AUTO\_INCREMENT)
  - `sourceid` (INT, DEFAULT NULL)
  - `message` (TEXT, NOT NULL)
  - `topic` (VARCHAR(255), NOT NULL)
  - `creationtime` (TIMESTAMP, DEFAULT CURRENT\_TIMESTAMP)

- **message\_variabledata**

  - `messageid` (INT, NOT NULL)
  - `variable` (VARCHAR(255), NOT NULL)
  - `data` (VARCHAR(255), NOT NULL)

- **sources**

  - `sourceid` (INT, PRIMARY KEY, AUTO\_INCREMENT)
  - `name` (TEXT)
  - `source_mqtt_key` (VARCHAR(255), NOT NULL)

---

## Usage

1. Set required environment variables (see above).
2. Start Docker Compose stack: `docker-compose up -d`.
3. Check service logs: `docker-compose logs -f mqtt_loader` or `docker-compose logs -f ha_loader`.
4. Manage database via phpMyAdmin: `http://localhost:8480`.

---

## License

```
MIT License
See LICENSE file for details.
```

