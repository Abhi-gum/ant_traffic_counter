import cv2
import os

VIDEO_PATH = "video/ants2.mp4"
OUTPUT_DIR = "dataset/images"

os.makedirs(OUTPUT_DIR, exist_ok=True)

cap = cv2.VideoCapture(VIDEO_PATH)

if not cap.isOpened():
    print("ERROR: Could not open ants2.mp4")
    exit()

fps = cap.get(cv2.CAP_PROP_FPS)

print("Video FPS:", fps)

frame_number = 0
saved_number = 0

# Save 1 frame every 15 frames
FRAME_INTERVAL = 15

while True:

    success, frame = cap.read()

    if not success:
        break

    if frame_number % FRAME_INTERVAL == 0:

        filename = os.path.join(
            OUTPUT_DIR,
            f"ant_frame_{saved_number:05d}.jpg"
        )

        cv2.imwrite(filename, frame)

        saved_number += 1

    frame_number += 1

cap.release()

print("--------------------------------")
print("FRAME EXTRACTION FINISHED")
print("--------------------------------")
print("Total frames saved:", saved_number)
print("--------------------------------")