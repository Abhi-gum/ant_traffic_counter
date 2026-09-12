from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

import os
import uuid

from detect import count_ants


app = Flask(__name__)
CORS(app)


UPLOAD_FOLDER = "uploads"
RESULT_FOLDER = "results"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)


@app.route("/")
def home():

    return "Ant Traffic Analyzer Backend Running"


@app.route("/analyze", methods=["POST"])
def analyze():

    try:

        if "video" not in request.files:

            return jsonify({
                "success": False,
                "error": "No video uploaded"
            }), 400

        video = request.files["video"]

        if video.filename == "":

            return jsonify({
                "success": False,
                "error": "No video selected"
            }), 400

        # --------------------------------
        # CREATE UNIQUE FILE NAME
        # --------------------------------

        filename = secure_filename(video.filename)

        unique_id = str(uuid.uuid4())

        input_filename = unique_id + "_" + filename

        input_path = os.path.join(
            UPLOAD_FOLDER,
            input_filename
        )

        # --------------------------------
        # SAVE UPLOADED VIDEO
        # --------------------------------

        video.save(input_path)

        # --------------------------------
        # OUTPUT VIDEO
        # --------------------------------

        output_filename = unique_id + "_result.mp4"

        output_path = os.path.join(
            RESULT_FOLDER,
            output_filename
        )

        # --------------------------------
        # RUN ANT DETECTION
        # --------------------------------

        total_ants = count_ants(
            input_path,
            output_path
        )

        # --------------------------------
        # CALCULATE TRAFFIC RATE
        # --------------------------------

        cap_fps = None

        import cv2

        cap = cv2.VideoCapture(input_path)

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)

        cap.release()

        if fps and fps > 0:

            duration_seconds = frame_count / fps

            duration_minutes = duration_seconds / 60

        else:

            duration_minutes = 10

        if duration_minutes > 0:

            traffic_rate = total_ants / duration_minutes

        else:

            traffic_rate = 0

        # --------------------------------
        # TRAFFIC LEVEL
        # --------------------------------

        if traffic_rate >= 10:

            traffic_status = "HIGH TRAFFIC"

        elif traffic_rate >= 5:

            traffic_status = "MEDIUM TRAFFIC"

        else:

            traffic_status = "LOW TRAFFIC"

        # --------------------------------
        # RETURN RESULT
        # --------------------------------

        return jsonify({

            "success": True,

            "count": total_ants,

            "traffic_rate": round(
                traffic_rate,
                1
            ),

            "duration": round(
                duration_minutes,
                1
            ),

            "status": traffic_status,

            "result_video": output_filename

        })

    except Exception as e:

        print("ERROR:", e)

        return jsonify({

            "success": False,
            "error": str(e)

        }), 500


if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )