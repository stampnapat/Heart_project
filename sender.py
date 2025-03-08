import network
import espnow
import time

Set up ESP32 as a Wi-Fi station
sta = network.WLAN(network.STA_IF)
sta.active(True)

Initialize ESP-NOW
esp = espnow.ESPNow()
esp.active(True)

Replace this with your Receiver's MAC address
receiver_mac = b'\xXX\xXX\xXX\xXX\xXX\xXX'
esp.add_peer(receiver_mac)

while True:
    msg = "Hello from ESP-NOW!"
    esp.send(receiver_mac, msg.encode())  # Send message
    print(f"Sent: {msg}")
    time.sleep(2)  # Send message every 2 seconds
#include <WiFi.h>
#include <esp_now.h>

void OnDataRecv(const uint8_t mac, const uint8_tincomingData, int len) {
    Serial.print("Received: ");
    Serial.println((char*)incomingData);
}

void setup() {
    Serial.begin(115200);
    WiFi.mode(WIFI_STA);

    if (esp_now_init() != ESP_OK) {
        Serial.println("ESP-NOW initialization failed!");
        return;
    }

    esp_now_register_recv_cb(OnDataRecv);
}

void loop() {
    // Do nothing, waiting for messages
}
ตงแอมเว — 4/3/2568 BE, 17:27
check mac address
#include <WiFi.h>

void setup() {
    Serial.begin(115200);
    WiFi.mode(WIFI_STA);  // Set ESP32 to Station mode
    Serial.print("ESP32 MAC Address: ");
    Serial.println(WiFi.macAddress());  // Print MAC Address
}

void loop() {
    // No need to run anything in loop
}
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
import network

sta = network.WLAN(network.STA_IF)  # Set Wi-Fi to Station mode
sta.active(True)  # Activate Wi-Fi
print("ESP32 MAC Address:", sta.config('mac'))
