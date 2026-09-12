from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import cv2
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

# Serve processed result videos back to the frontend
@app.route("/results/<filename>")
def get_result_video(filename):
    return send_from_directory(RESULT_FOLDER, filename)

@app.route("/analyze", methods=["POST"])
def analyze():
    input_path = None
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

        filename = secure_filename(video.filename)
        unique_id = str(uuid.uuid4())
        input_filename = unique_id + "_" + filename
        input_path = os.path.join(UPLOAD_FOLDER, input_filename)

        # Save uploaded video
        video.save(input_path)

        # Output video path
        output_filename = unique_id + "_result.mp4"
        output_path = os.path.join(RESULT_FOLDER, output_filename)

        # Run ant detection
        total_ants = count_ants(input_path, output_path)

        # Calculate traffic rate
        cap = cv2.VideoCapture(input_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        cap.release()

        if fps and fps > 0:
            duration_seconds = frame_count / fps
            duration_minutes = duration_seconds / 60
        else:
            duration_minutes = 10

        traffic_rate = total_ants / duration_minutes if duration_minutes > 0 else 0

        # Traffic level status
        if traffic_rate >= 10:
            traffic_status = "HIGH TRAFFIC"
        elif traffic_rate >= 5:
            traffic_status = "MEDIUM TRAFFIC"
        else:
            traffic_status = "LOW TRAFFIC"

        # Generate full URL for the result video
        base_url = request.host_url.rstrip('/')
        result_video_url = f"{base_url}/results/{output_filename}"

        return jsonify({
            "success": True,
            "count": total_ants,
            "traffic_rate": round(traffic_rate, 1),
            "duration": round(duration_minutes, 1),
            "status": traffic_status,
            "result_video": result_video_url
        })

    except Exception as e:
        print("ERROR:", e)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

    finally:
        # Clean up input file to save server storage
        if input_path and os.path.exists(input_path):
            try:
                os.remove(input_path)
            except Exception:
                pass

if __name__ == "__main__":
    # Production environment settings (reads cloud port automatically)
    port = int(os.environ.get("PORT", 10000))
    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )