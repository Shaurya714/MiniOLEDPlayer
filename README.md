# MiniOLEDPlayer

A custom-built video player that displays a monochrome animation on a 128×64 OLED using an ESP32. The project converts a video into compact, frame-by-frame bitmap data and plays it back from the ESP32's flash filesystem.

> **Status:** Under development — firmware compilation and video conversion are complete. Physical display playback and timing are awaiting hardware testing.

## Overview

MiniOLEDPlayer explores the intersection of embedded systems, image processing, and low-level display rendering.

Instead of decoding an MP4 directly on the ESP32, the video is preprocessed on a computer into monochrome bitmap frames. The ESP32 reads these frames from its SPIFFS filesystem and renders them on an OLED display.

### Features

- Custom Python video-to-bitmap converter using OpenCV and NumPy
- Aspect-ratio-preserving video scaling for a 128×64 display
- Monochrome frame conversion with a black background
- SPIFFS-based video storage
- Arduino firmware developed with PlatformIO
- Target playback rate of 30 FPS
- Automatic looping when the video reaches its final frame

## Hardware

| Component | Specification |
|---|---|
| Microcontroller | ESP32 NodeMCU, 30-pin board |
| Display | Tishvi 1.3-inch SH1106 OLED |
| Resolution | 128×64 pixels |
| Interface | I²C, four-pin display |
| Firmware framework | Arduino |
| Development environment | VS Code + PlatformIO |

**Planned I²C connections:** GPIO 21 for SDA and GPIO 22 for SCL. Confirm the board and display pin labels before wiring.

## Software Stack

- **C++ / Arduino** — embedded playback firmware
- **Python** — video preprocessing
- **OpenCV** — video decoding and frame processing
- **NumPy** — bitmap conversion and bit packing
- **U8g2** — OLED display rendering
- **PlatformIO** — firmware building and filesystem image generation
- **SPIFFS** — storing the converted video in flash

## How It Works

```text
Source MP4
    |
    v
Python video converter
    |
    v
Resize and convert frames to monochrome
    |
    v
Pack each 128×64 frame into 1,024 bytes
    |
    v
SPIFFS filesystem image
    |
    v
ESP32 reads frames from flash
    |
    v
SH1106 OLED displays the animation
```

A 128×64 monochrome frame requires:

`128 × 64 ÷ 8 = 1,024 bytes`

The current 309-frame video therefore produces 316,416 bytes of raw bitmap data.

## Project Structure

```text
MiniOLEDPlayer/
├── converter/
│   └── video_converter.py
├── data/
│   └── video.bin              # Generated asset, not committed
├── include/
├── lib/
├── output/
│   ├── preview.png            # Generated preview, not committed
│   └── video.bin              # Generated video, not committed
├── src/
│   └── main.cpp
├── test/
├── platformio.ini
├── .gitignore
└── README.md
```

The source video is intentionally excluded from version control. Place your own compatible video in the project root using the filename expected by the converter.

## Getting Started

### 1. Prerequisites

Install:

- [Visual Studio Code](https://code.visualstudio.com/)
- [PlatformIO IDE](https://platformio.org/install/ide?install=vscode)
- [Python](https://www.python.org/downloads/)
- The Python packages `opencv-python` and `numpy`

Install the Python dependencies:

```bash
python -m pip install opencv-python numpy
```

### 2. Prepare the video

Place your source video in the project root using the filename configured in `converter/video_converter.py`.

Run the converter from the project root:

```bash
python converter/video_converter.py
```

The converter generates the packed bitmap video and a preview image. Review the preview before flashing the device.

### 3. Build the firmware

From the project root:

```bash
pio run
```

### 4. Build the filesystem image

Generate the SPIFFS image containing the converted video:

```bash
pio run --target buildfs
```

Ensure the generated `video.bin` is in the configured filesystem data directory before building the filesystem image.

### 5. Flash the ESP32

Connect the ESP32 over USB and identify the correct serial port.

Upload the firmware:

```bash
pio run --target upload
```

Upload the filesystem image:

```bash
pio run --target uploadfs
```

The display must be wired correctly before testing playback. These steps describe the intended workflow; physical hardware validation is still pending.

## Performance Notes

At 30 FPS, the target frame interval is approximately 33.3 milliseconds. Actual playback performance depends on filesystem reads, bitmap rendering, display transfer time, and I²C speed.

The 30 FPS value is a target, not a verified measurement.

## Current Limitations

- Playback has not yet been validated on the physical display.
- Actual frame rate and animation smoothness remain unmeasured.
- The original MP4 is not included in the repository.
- Audio is not handled by the ESP32; it is intended to play separately.

## Future Improvements

- Measure and optimize real-world playback performance.
- Improve frame pacing and eliminate visible stuttering.
- Add configurable playback speed.
- Document verified wiring and hardware test results.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

The license applies to this project's original code. Third-party libraries and other assets remain subject to their respective licenses.
