import cv2
import numpy as np
import math

VIDEO_PATH = "../video/ants2.mp4"
OUTPUT_PATH = "../video/ant_traffic_result.mp4"

LINE_X = 424

MIN_AREA = 3
MAX_AREA = 80

MAX_DISTANCE = 30
MAX_MISSED = 6


# -----------------------------
# OPEN VIDEO
# -----------------------------

cap = cv2.VideoCapture(VIDEO_PATH)

if not cap.isOpened():
    print("ERROR: Cannot open ants2.mp4")
    exit()

fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

print("--------------------------------")
print("ANT TRAFFIC COUNTER")
print("--------------------------------")
print("Video:", VIDEO_PATH)
print("Resolution:", width, "x", height)
print("FPS:", round(fps, 2))
print("Frames:", total_frames)
print("--------------------------------")


# -----------------------------
# CREATE BACKGROUND
# -----------------------------

print("Creating background...")

sample_count = 30

frame_indexes = np.linspace(
    0,
    total_frames - 1,
    sample_count
).astype(int)

background_frames = []

for index in frame_indexes:

    cap.set(cv2.CAP_PROP_POS_FRAMES, int(index))

    success, frame = cap.read()

    if success:

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        background_frames.append(gray)


background = np.median(
    np.stack(background_frames),
    axis=0
).astype(np.uint8)

print("Background created.")


# -----------------------------
# OUTPUT VIDEO
# -----------------------------

fourcc = cv2.VideoWriter_fourcc(*"mp4v")

out = cv2.VideoWriter(
    OUTPUT_PATH,
    fourcc,
    fps,
    (width, height)
)


# -----------------------------
# TRACKING
# -----------------------------

tracks = {}

next_id = 0
total_count = 0


# -----------------------------
# RESET VIDEO
# -----------------------------

cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

frame_number = 0


# -----------------------------
# MAIN LOOP
# -----------------------------

while True:

    success, frame = cap.read()

    if not success:
        break

    frame_number += 1


    # -------------------------
    # GRAYSCALE
    # -------------------------

    gray = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )


    # -------------------------
    # BACKGROUND DIFFERENCE
    # -------------------------

    difference = cv2.absdiff(
        gray,
        background
    )


    # -------------------------
    # THRESHOLD
    # -------------------------

    _, mask = cv2.threshold(
        difference,
        12,
        255,
        cv2.THRESH_BINARY
    )


    # -------------------------
    # REMOVE NOISE
    # -------------------------

    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (2, 2)
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_OPEN,
        kernel
    )


    # -------------------------
    # FIND CONTOURS
    # -------------------------

    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )


    detections = []


    for contour in contours:

        area = cv2.contourArea(contour)

        if area < MIN_AREA:
            continue

        if area > MAX_AREA:
            continue


        x, y, w, h = cv2.boundingRect(contour)


        if w > 25:
            continue

        if h > 20:
            continue

        if w < 2:
            continue

        if h < 2:
            continue


        center_x = x + w // 2
        center_y = y + h // 2


        detections.append(
            (
                center_x,
                center_y,
                x,
                y,
                w,
                h
            )
        )


    # -------------------------
    # UPDATE TRACKS
    # -------------------------

    updated_tracks = {}

    used_detections = set()


    for track_id, track in tracks.items():

        old_x = track["x"]
        old_y = track["y"]

        best_index = None
        best_distance = MAX_DISTANCE


        for i, detection in enumerate(detections):

            if i in used_detections:
                continue


            new_x = detection[0]
            new_y = detection[1]


            distance = math.sqrt(
                (new_x - old_x) ** 2 +
                (new_y - old_y) ** 2
            )


            if distance < best_distance:

                best_distance = distance
                best_index = i


        if best_index is not None:

            detection = detections[best_index]

            new_x = detection[0]
            new_y = detection[1]

            used_detections.add(best_index)


            old_position = old_x


            # -------------------------
            # CHECK LINE CROSSING
            # -------------------------

            crossed = False


            if old_position < LINE_X and new_x >= LINE_X:
                crossed = True


            if old_position > LINE_X and new_x <= LINE_X:
                crossed = True


            if crossed and not track["counted"]:

                total_count += 1

                track["counted"] = True

                print(
                    "Ant counted:",
                    total_count
                )


            updated_tracks[track_id] = {

                "x": new_x,

                "y": new_y,

                "missed": 0,

                "counted": track["counted"],

                "age": track["age"] + 1
            }


        else:

            track["missed"] += 1


            if track["missed"] <= MAX_MISSED:

                updated_tracks[track_id] = track


    # -------------------------
    # CREATE NEW TRACKS
    # -------------------------

    for i, detection in enumerate(detections):

        if i in used_detections:
            continue


        new_x = detection[0]
        new_y = detection[1]


        updated_tracks[next_id] = {

            "x": new_x,

            "y": new_y,

            "missed": 0,

            "counted": False,

            "age": 1
        }


        next_id += 1


    tracks = updated_tracks


    # -------------------------
    # DRAW TRACKS
    # -------------------------

    for track_id, track in tracks.items():

        x = track["x"]
        y = track["y"]


        if track["age"] >= 2:

            cv2.circle(
                frame,
                (x, y),
                4,
                (0, 255, 0),
                -1
            )


            cv2.putText(
                frame,
                str(track_id),
                (x + 5, y - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.35,
                (0, 255, 0),
                1
            )


    # -------------------------
    # COUNTING LINE
    # -------------------------

    cv2.line(
        frame,
        (LINE_X, 0),
        (LINE_X, height),
        (0, 0, 255),
        2
    )


    cv2.putText(
        frame,
        "COUNTING LINE",
        (LINE_X - 70, 25),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (0, 0, 255),
        1
    )


    # -------------------------
    # COUNT DISPLAY
    # -------------------------

    cv2.rectangle(
        frame,
        (10, 10),
        (240, 65),
        (0, 0, 0),
        -1
    )


    cv2.putText(
        frame,
        f"ANTS: {total_count}",
        (25, 48),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 255),
        2
    )


    # -------------------------
    # SAVE FRAME
    # -------------------------

    out.write(frame)


    # -------------------------
    # PROGRESS
    # -------------------------

    if frame_number % max(1, int(fps * 10)) == 0:

        progress = (
            frame_number / total_frames
        ) * 100

        print(
            f"Processing: {progress:.1f}%"
        )


# -----------------------------
# FINISH
# -----------------------------

cap.release()
out.release()

print()
print("--------------------------------")
print("DETECTION FINISHED")
print("--------------------------------")
print("TOTAL ANTS:", total_count)
print("RESULT:", OUTPUT_PATH)
print("--------------------------------")