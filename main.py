# main.py
from flask import Flask, request, jsonify
from transcriber import transcribe_audio
from extractor import extract_workout_data
from database import workouts_collection  
from auth import auth_bp
from auth_utils import token_required
from pymongo import MongoClient
import os

app = Flask(__name__)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(
    MONGO_URI,
    tls=True,
    tlsAllowInvalidCertificates=False,
    serverSelectionTimeoutMS=5000
)

@app.route("/upload-audio", methods=["POST"])
@token_required
def upload_audio(user_id):
    if "audio" not in request.files:
        return jsonify({"error": "No 'audio' file in request"}), 400

    audio_file = request.files["audio"]

    try:
        transcript_text = transcribe_audio(audio_file)
        print("Transcription:", transcript_text)
        
        extracted_model = extract_workout_data(transcript_text)
        workout_dict = extracted_model.model_dump()  # Convert Pydantic model to dict
        # attach user id to workout
        workout_dict["user_id"] = user_id
        result = workouts_collection.insert_one(workout_dict)
        inserted_id_str = str(result.inserted_id)
        workout_dict["_id"] = inserted_id_str

        return jsonify({
            "workout_data": workout_dict,
            "inserted_id": inserted_id_str
        }), 200

    except Exception as e:
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500

@app.route("/workouts", methods=["GET", "POST"])
@token_required
def workouts(user_id):
    if request.method == "GET":
        # Retrieve workouts for this user only
        all_docs = workouts_collection.find({"user_id": user_id})
        workouts = []
        for doc in all_docs:
            doc["_id"] = str(doc["_id"])
            workouts.append(doc)
        return jsonify(workouts), 200

    if request.method == "POST":
        data = request.get_json()  # { exercise, reps, weight, date }
        # attach user id
        data["user_id"] = user_id
        result = workouts_collection.insert_one(data)
        data["_id"] = str(result.inserted_id)
        return jsonify(data), 201

# Register our auth blueprint
app.register_blueprint(auth_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
