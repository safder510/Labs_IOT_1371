#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>
#include <time.h>

// WiFi Credentials
const char* ssid = "TECNO SPARK 8C";
const char* password = "safder@510";

// Firebase Configuration
const String FIREBASE_HOST = "iot-lab-11-1371-default-rtdb.firebaseio.com";
const String FIREBASE_AUTH = "hxuQWFojwCD3HaxWpwmbrp2tdASeIZZZOjJhZTxq";
const String FIREBASE_PATH = "/sensor_data_1371.json";

// Firebase Configuration
// const String FIREBASE_HOST = "iot-lab-11-1371-default-rtdb.firebaseio.com";
// const String FIREBASE_AUTH = "hxuQWFojwCD3HaxWpwmbrp2tdASeIZZZOjJhZTxq";
// const String FIREBASE_PATH = "/sensor_data_1371.json";

// DHT Sensor
#define DHTPIN 4       // GPIO4
#define DHTTYPE DHT11  // DHT11 or DHT22
DHT dht(DHTPIN, DHTTYPE);

// Timing
const unsigned long SEND_INTERVAL = 10000;  // 10 seconds
const unsigned long SENSOR_DELAY = 2000;    // 2 seconds

// Timing variables
unsigned long lastSendTime = 0;
unsigned long lastReadTime = 0;

void setup() {
  Serial.begin(115200);
  Serial.println("\nESP32-S3 DHT11 Firebase Monitor");

  dht.begin();
  connectWiFi();
  initNTP();
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    connectWiFi();
  }

  if (millis() - lastReadTime >= SENSOR_DELAY) {
    float temp, hum;
    if (readDHT(&temp, &hum)) {
      if (millis() - lastSendTime >= SEND_INTERVAL) {
        sendToFirebase(temp, hum);
        lastSendTime = millis();
      }
    }
    lastReadTime = millis();
  }
}

// ======= WiFi Connection ======= //
void connectWiFi() {
  Serial.print("Connecting to WiFi");
  WiFi.disconnect(true);
  WiFi.begin(ssid, password);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 15) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi Connected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nWiFi Connection Failed!");
  }
}

// ======= NTP Initialization ======= //
void initNTP() {
  configTime(18000, 0, "pool.ntp.org");  // GMT+5 (Pakistan Standard Time)
  Serial.println("Waiting for NTP time sync...");
  struct tm timeinfo;
  while (!getLocalTime(&timeinfo)) {
    Serial.println("Failed to obtain time");
    delay(1000);
  }
  Serial.println("Time synchronized");
}

// ======= DHT Sensor Functions ======= //
bool readDHT(float* temp, float* hum) {
  *temp = dht.readTemperature();
  *hum = dht.readHumidity();

  if (isnan(*temp) || isnan(*hum)) {
    Serial.println("DHT read failed! Retrying...");
    return false;
  }

  Serial.printf("DHT Read: %.1f°C, %.1f%%\n", *temp, *hum);
  return true;
}

// ======= Firebase Function ======= //
void sendToFirebase(float temp, float hum) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Cannot send - WiFi disconnected");
    return;
  }

  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    Serial.println("Failed to get local time");
    return;
  }

  char timeStr[30];
  strftime(timeStr, sizeof(timeStr), "%Y-%m-%d %H:%M:%S", &timeinfo);

  String jsonPayload = "{\"temperature\":" + String(temp) +
                       ",\"humidity\":" + String(hum) +
                       ",\"timestamp\":\"" + String(timeStr) + "\"}";

  Serial.println("Sending to Firebase...");
  Serial.println(jsonPayload);

  HTTPClient http;
  String url = "https://" + FIREBASE_HOST + FIREBASE_PATH + "?auth=" + FIREBASE_AUTH;
  http.begin(url);
  http.addHeader("Content-Type", "application/json");

  int httpCode = http.POST(jsonPayload);
  if (httpCode == HTTP_CODE_OK || httpCode == HTTP_CODE_ACCEPTED) {
    Serial.println("Firebase update successful");
  } else {
    Serial.printf("Firebase error: %d\n", httpCode);
  }

  http.end();
}
