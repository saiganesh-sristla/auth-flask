from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import bcrypt
from dotenv import load_dotenv
import os

load_dotenv() 

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# MongoDB setup
client = MongoClient(os.getenv("MONGO_URI"))
db = client["pediatricianDB"]
users_collection = db["users"]

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    # Check if email already exists
    if users_collection.find_one({"email": data["email"]}):
        return jsonify({"success": False, "message": "Email already exists."}), 400

    # Hash the password
    hashed_password = bcrypt.hashpw(data["password"].encode("utf-8"), bcrypt.gensalt())
    
    # Create the user document
    user = {
        "email": data["email"],
        "phone_number": data["phone_number"],
        "first_name": data["first_name"],
        "last_name": data["last_name"],
        "clinic_name": data["clinic_name"],
        "specialization": data["specialization"],
        "password": hashed_password,
    }
    users_collection.insert_one(user)
    return jsonify({"success": True, "message": "Signup successful!"}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = users_collection.find_one({"email": data["email"]})
    
    if not user:
        return jsonify({"success": False, "message": "Invalid email or password."}), 401
    
    # Check the password
    if bcrypt.checkpw(data["password"].encode("utf-8"), user["password"]):
        return jsonify({"success": True, "message": "Login successful!", "user": {
            "email": user["email"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "clinic_name": user["clinic_name"],
            "specialization": user["specialization"],
        }}), 200
    else:
        return jsonify({"success": False, "message": "Invalid email or password."}), 401

if __name__ == "__main__":
    app.run(debug=True)
