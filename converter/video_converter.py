
from pathlib import Path

import cv2
import numpy as np


# Project paths
PROJECT_DIR = Path(__file__).resolve().parent.parent
VIDEO_PATH = PROJECT_DIR / "love me not.mp4"
OUTPUT_DIR = PROJECT_DIR / "output"
OUTPUT_PATH = OUTPUT_DIR / "video.bin"
PREVIEW_PATH = OUTPUT_DIR / "preview.png"

# OLED dimensions
OLED_WIDTH = 128
OLED_HEIGHT = 64

# Preserve the source video's frame rate.
TARGET_FPS = None

# Dark artwork becomes illuminated pixels on the OLED.
THRESHOLD = 150


def main():
    if not VIDEO_PATH.exists():
        print(f"ERROR: Video not found:\n{VIDEO_PATH}")
        print(
            "\nPlace your video named "
            "'love me not.mp4' in the project root folder."
        )
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    video = cv2.VideoCapture(str(VIDEO_PATH))

    if not video.isOpened():
        print("ERROR: OpenCV could not open the video.")
        return

    try:
        source_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        source_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        source_fps = video.get(cv2.CAP_PROP_FPS)
        source_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

        if source_width <= 0 or source_height <= 0:
            print("ERROR: Invalid source video dimensions.")
            return

        if source_fps <= 0:
            print("ERROR: Invalid source frame rate.")
            return

        fps = TARGET_FPS if TARGET_FPS else source_fps

        # Fit the entire video into the OLED without cropping
        # or changing its aspect ratio.
        scale = min(
            OLED_WIDTH / source_width,
            OLED_HEIGHT / source_height,
        )

        fitted_width = max(1, round(source_width * scale))
        fitted_height = max(1, round(source_height * scale))

        left = (OLED_WIDTH - fitted_width) // 2
        top = (OLED_HEIGHT - fitted_height) // 2

        print(f"Input: {VIDEO_PATH.name}")
        print(
            f"Source: {source_width}x{source_height} "
            f"at {source_fps:.2f} FPS"
        )
        print(f"Source frames: {source_frames}")
        print(f"Output frame size: {OLED_WIDTH}x{OLED_HEIGHT}")
        print(f"Video area: {fitted_width}x{fitted_height}")
        print(f"Output frame rate: {fps:.2f} FPS")
        print("Converting frames...")

        first_preview = None
        processed_frames = 0

        with OUTPUT_PATH.open("wb") as output_file:
            while True:
                success, frame = video.read()

                if not success:
                    break

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                resized = cv2.resize(
                    gray,
                    (fitted_width, fitted_height),
                    interpolation=cv2.INTER_AREA,
                )

                # Dark artwork is ON; bright background is OFF.
                artwork = (resized < THRESHOLD).astype(np.uint8)

                oled_frame = np.zeros(
                    (OLED_HEIGHT, OLED_WIDTH),
                    dtype=np.uint8,
                )

                oled_frame[
                    top:top + fitted_height,
                    left:left + fitted_width,
                ] = artwork

                if first_preview is None:
                    first_preview = oled_frame.copy()

                # U8g2 drawXBMP expects XBM-style bit ordering:
                # the leftmost pixel occupies the least-significant bit.
                packed = np.packbits(
                    oled_frame,
                    axis=1,
                    bitorder="little",
                )

                output_file.write(packed.tobytes())
                processed_frames += 1

        if processed_frames == 0:
            print("ERROR: No frames were decoded.")
            return

        if first_preview is not None:
            # OpenCV uses BGR channel ordering.
            preview = np.zeros(
                (OLED_HEIGHT, OLED_WIDTH, 3),
                dtype=np.uint8,
            )

            preview[first_preview == 1] = (255, 100, 0)
            cv2.imwrite(str(PREVIEW_PATH), preview)

        frame_size = OLED_WIDTH * OLED_HEIGHT // 8
        expected_size = processed_frames * frame_size
        actual_size = OUTPUT_PATH.stat().st_size

        print("\nConversion complete.")
        print(f"Frames processed: {processed_frames}")
        print(f"Frame size: {frame_size:,} bytes")
        print(f"Binary file size: {actual_size:,} bytes")
        print(f"Expected size: {expected_size:,} bytes")
        print(f"Binary output: {OUTPUT_PATH}")
        print(f"Preview image: {PREVIEW_PATH}")

        if actual_size != expected_size:
            print("ERROR: Output size does not match the expected size.")
            return

        print("Output size validation passed.")
        print("Bitmap bit order: XBM-compatible (LSB first).")

    finally:
        video.release()


if __name__ == "__main__":
    main()
