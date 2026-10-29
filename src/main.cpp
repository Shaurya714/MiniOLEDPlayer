
#include <Arduino.h>
#include <Wire.h>
#include <SPIFFS.h>
#include <U8g2lib.h>

// SH1106 128x64 monochrome OLED using I2C.
U8G2_SH1106_128X64_NONAME_F_HW_I2C oled(
    U8G2_R0,
    U8X8_PIN_NONE
);

constexpr uint16_t SCREEN_WIDTH = 128;
constexpr uint16_t SCREEN_HEIGHT = 64;
constexpr size_t FRAME_BYTES = SCREEN_WIDTH * SCREEN_HEIGHT / 8;

constexpr uint16_t VIDEO_FPS = 30;
constexpr uint32_t FRAME_INTERVAL_US = 1000000UL / VIDEO_FPS;

File videoFile;
uint8_t frameBuffer[FRAME_BYTES];

uint32_t frameCount = 0;
uint32_t lastFrameTime = 0;
bool playbackReady = false;

void showError(const char* message) {
    Serial.println(message);

    oled.clearBuffer();
    oled.setFont(u8g2_font_6x10_tf);
    oled.drawStr(0, 14, "Video player error:");
    oled.drawStr(0, 30, message);
    oled.sendBuffer();
}

void setup() {
    Serial.begin(115200);
    delay(300);

    Wire.begin(21, 22);

    oled.begin();
    oled.setContrast(255);
    oled.clearBuffer();
    oled.setFont(u8g2_font_6x10_tf);
    oled.drawStr(0, 14, "MiniOLEDPlayer");
    oled.drawStr(0, 30, "Loading video...");
    oled.sendBuffer();

    Serial.println();
    Serial.println("MiniOLEDPlayer starting...");

    if (!SPIFFS.begin(false)) {
        showError("SPIFFS mount failed");
        return;
    }

    videoFile = SPIFFS.open("/video.bin", FILE_READ);

    if (!videoFile) {
        showError("video.bin not found");
        return;
    }

    const size_t videoSize = videoFile.size();

    if (videoSize == 0 || videoSize % FRAME_BYTES != 0) {
        showError("Invalid video file");
        videoFile.close();
        return;
    }

    frameCount = videoSize / FRAME_BYTES;

    Serial.printf("Video size: %u bytes\n",
                  static_cast<unsigned int>(videoSize));
    Serial.printf("Frame count: %u\n",
                  static_cast<unsigned int>(frameCount));
    Serial.printf("Frame rate target: %u FPS\n", VIDEO_FPS);

    playbackReady = true;
    lastFrameTime = micros();

    Serial.println("Playback ready.");
}

void loop() {
    if (!playbackReady) {
        delay(1000);
        return;
    }

    const uint32_t now = micros();
    const uint32_t elapsed = now - lastFrameTime;

    if (elapsed < FRAME_INTERVAL_US) {
        delayMicroseconds(FRAME_INTERVAL_US - elapsed);
    }

    lastFrameTime = micros();

    if (videoFile.available() < static_cast<int>(FRAME_BYTES)) {
        if (!videoFile.seek(0)) {
            showError("Video rewind failed");
            playbackReady = false;
            videoFile.close();
            return;
        }
    }

    const size_t bytesRead = videoFile.read(frameBuffer, FRAME_BYTES);

    if (bytesRead != FRAME_BYTES) {
        showError("Video read failed");
        playbackReady = false;
        videoFile.close();
        return;
    }

    // The converter packs pixels left-to-right, MSB first.
    // U8g2 draws this 1-bit bitmap directly to the display buffer.
    oled.clearBuffer();
    oled.drawXBMP(
        0,
        0,
        SCREEN_WIDTH,
        SCREEN_HEIGHT,
        frameBuffer
    );
    oled.sendBuffer();
}
