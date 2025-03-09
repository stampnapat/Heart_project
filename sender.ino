#include <Arduino_JSON.h>

#include <Wire.h>
#include "MAX30105.h"
#include "heartRate.h"
#include <driver/i2s.h>
#include <math.h>
#include <esp_now.h>
#include <WiFi.h>
MAX30105 particleSensor;
uint8_t receiverMAC[] = {0x68, 0xB6, 0xB3, 0x38, 0x03, 0x88};
JSONVar jsonData;
void OnDataSent(const uint8_t *mac_addr, esp_now_send_status_t status) {
    Serial.print("Send Status: ");
    Serial.println(status == ESP_NOW_SEND_SUCCESS ? "Success" : "Fail");
}
// 🔴 กำหนดขา I2S สำหรับ INMP441
#define I2S_WS   15  // LRCL
#define I2S_BCK  2   // BCLK
#define I2S_DIN  13  // DOUT

// 🔴 กำหนดขา I2C สำหรับ MAX30105
#define SDA_PIN  47
#define SCL_PIN  48

// ✅ ตัวแปรเก็บค่าหัวใจ
const byte RATE_SIZE = 4;
byte rates[RATE_SIZE];
byte rateSpot = 0;
long lastBeat = 0;
float beatsPerMinute;
int beatAvg;

// 📌 ฟังก์ชันติดตั้ง I2S
void setupI2S() {
    i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
        .sample_rate = 44100,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
        .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
        .communication_format = I2S_COMM_FORMAT_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 8,
        .dma_buf_len = 64,
        .use_apll = false
    };

    i2s_pin_config_t pin_config = {
        .bck_io_num = I2S_BCK,
        .ws_io_num = I2S_WS,
        .data_out_num = I2S_PIN_NO_CHANGE,
        .data_in_num = I2S_DIN
    };

    i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
    i2s_set_pin(I2S_NUM_0, &pin_config);
    i2s_zero_dma_buffer(I2S_NUM_0);
}

// 📌 ฟังก์ชันคำนวณ dB จากเสียงที่ได้รับ
float calculateDB(int32_t *samples, int sampleCount) {
    double sumSq = 0;
    for (int i = 0; i < sampleCount; i++) {
        sumSq += pow(abs(samples[i]), 2);
    }
    double rms = sqrt(sumSq / sampleCount);
    float dB = (rms > 0) ? 20.0 * log10(rms) : 0;
    return round(dB * 100) / 100;
}

void setup() {
    Serial.begin(115200);
    Serial.println("🔊 กำลังเริ่มต้นระบบ...");
    Wire.begin(48, 47);
    // ✅ ตั้งค่า I2S
    setupI2S();
    Serial.println("✅ I2S พร้อมใช้งาน");

    // ✅ ตั้งค่า I2C และ MAX30105
    Wire.begin(SDA_PIN, SCL_PIN);
    if (!particleSensor.begin(Wire, I2C_SPEED_FAST, 0x57)) {
        Serial.println("❌ MAX30105 ไม่พบเซ็นเซอร์! กรุณาตรวจสอบการเชื่อมต่อ");
        while (1);
    }
    
    Serial.println("❤️ วัดชีพจร... กรุณาวางนิ้วบนเซ็นเซอร์");
    particleSensor.setup();
    particleSensor.setPulseAmplitudeRed(0x0A);
    particleSensor.setPulseAmplitudeGreen(0);

    WiFi.mode(WIFI_STA);
    if (esp_now_init() != ESP_OK) {
        Serial.println("ESP-NOW Init Failed");
        return;
    }
    esp_now_register_send_cb(OnDataSent);

    esp_now_peer_info_t peerInfo;
    memcpy(peerInfo.peer_addr, receiverMAC, 6);
    peerInfo.channel = 0;
    peerInfo.encrypt = false;
    if (esp_now_add_peer(&peerInfo) != ESP_OK) {
        Serial.println("Failed to add peer");
        return;
    }

}

void loop() {
    // 📌 อ่านค่าเสียงจาก INMP441
    int32_t samples[128];
    size_t bytesRead;
    i2s_read(I2S_NUM_0, samples, sizeof(samples), &bytesRead, portMAX_DELAY);
    float dbLevel = calculateDB(samples, 128);

    // 📌 อ่านค่า IR และ Red จาก MAX30105
    long irValue = particleSensor.getIR();
    long redValue = particleSensor.getRed();

        if (checkForBeat(irValue) == true) {
        long delta = millis() - lastBeat;
        lastBeat = millis();
        beatsPerMinute = 60 / (delta / 1000.0);

        if (beatsPerMinute < 255 && beatsPerMinute > 20) {
            rates[rateSpot++] = (byte)beatsPerMinute;
            rateSpot %= RATE_SIZE;

            // คำนวณค่าเฉลี่ยของอัตราการเต้นของหัวใจ
            beatAvg = 0;
            for (byte x = 0; x < RATE_SIZE; x++) {
                beatAvg += rates[x];
            }
            beatAvg /= RATE_SIZE;
        }
    }

    // 📌 แสดงค่าบน Serial Monitor
    // Serial.print("🔊 dB: ");
    // Serial.print(dbLevel);
    // Serial.print(" | ❤️ BPM: ");
    // Serial.print(irValue);
    // Serial.print(" (Avg: ");
    // Serial.print(beatAvg);
    // Serial.println(")");
////

    jsonData["redValue"] = redValue;
    jsonData["irValue"] = irValue;
    jsonData["heartrate"] = beatsPerMinute;
    jsonData["avgHr"] = beatAvg;
    jsonData["db"] = dbLevel;

    String jsonString = JSON.stringify(jsonData);
    uint8_t *buffer = (uint8_t*) jsonString.c_str();
    size_t sizeBuff = jsonString.length();

    esp_err_t result = esp_now_send(receiverMAC, buffer, sizeBuff);
    if (result == ESP_OK) {
        Serial.println("Sent Successfully: " + jsonString);
    } else {
        //Serial.println("Send Failed");
    }


      // หน่วงเวลา 500ms
}
