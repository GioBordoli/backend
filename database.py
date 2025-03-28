import os
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(
    MONGO_URI,
    tls=True,
    tlsAllowInvalidCertificates=False,
    serverSelectionTimeoutMS=5000
)
db = client["gymtracking"]

# Collections       
workouts_collection = db["workouts"]
users_collection = db["users"]
