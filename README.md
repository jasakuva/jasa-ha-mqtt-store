 [English version](readme_en.md)

# HA ja MQTT data MySQL tietokantaan

**Lyhyt kuvaus:** Tämä Python-projekti hakee Home Assistant -järjestelmästä entityjen tilat heti niiden muuttuessa sekä kuuntelee MQTT-jonon viestejä ja tallentaa molempien tiedot MySQL-tietokantaan.

---

## Ominaisuudet

- Kerää Home Assistant -entityjen arvot heti muutoksen tapahtuessa.
- Kuuntelee MQTT-aihetta ja prosessoi saapuvat viestit.
- Tallentaa sekä entity- että MQTT-dataan liittyvät rivit MySQL-tietokantaan.
- Käytettävissä Docker Compose -kokoonpanossa (kaikki palvelut kontteina).

---

## Arkitehtuuri

Projektin palvelut ajetaan neljässä Docker-kontissa (Docker Compose):

1. **MySQL** — tietokanta, johon data tallennetaan.
2. **phpMyAdmin** — tietokannan hallintaan selainkäyttöliittymän kautta.
3. **MQTT-viestien siirtäjä** — Python-palvelu, joka kuuntelee MQTT-brokeria ja tallentaa viestit tietokantaan.
4. **Home Assistant -entityjen siirtäjä** — Python-palvelu, joka kuuntelee Home Assistantin WebSocket-rajapintaa ja tallentaa entity-arvot muutosten mukaan.

---

## Asennus ja käynnistys (Docker Compose)

Tämä projekti on suunniteltu ajettavaksi Docker Composella. Alla valmis `docker-compose.yml`:

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
      HA_TOKEN: YUOR_HA_TOKEN
    depends_on:
      - mysql

volumes:
  jasa-ha-store:
```

**Käynnistä palvelut:**

```bash
docker-compose up -d
```

---

## Konfiguraatioparametrit

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

## Tietokantataulut ja sarakkeet

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

## Käyttö

1. Määritä tarvittavat ympäristömuuttujat (ks. yllä).
2. Käynnistä Docker Compose -pino: `docker-compose up -d`.
3. Tarkista palvelujen lokit: `docker-compose logs -f mqtt_loader` tai `docker-compose logs -f ha_loader`.
4. Hallitse tietokantaa phpMyAdminilla: `http://localhost:8480`.

---

## Lisenssi

```
MIT License
See LICENSE file for details.
```

