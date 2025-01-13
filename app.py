import os
import sqlite3
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import base64
from io import BytesIO
from PIL import Image

from flask_cors import CORS


# Initialize Flask app
app = Flask(__name__, static_folder='static')
# Enable CORS for all routes
CORS(app)
# Set the database filename
DATABASE = 'predictions.db'

# Set the upload folder for images
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Serve images from the uploads folder
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Create a database connection
def get_db():
    conn = sqlite3.connect(DATABASE)
    return conn

# Create table to store predictions if it doesn't exist
def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY,
            image_name TEXT,
            classification TEXT
        )
    """)
    conn.commit()
    conn.close()

# Call init_db() to initialize the database
init_db()

@app.route('/')
def index():
    return render_template('index.html')  # Serve the frontend

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    prediction = data.get("prediction", "")
    image_data = data.get("image_data", "")

    if not prediction or not image_data:
        return jsonify({"error": "No prediction data or image received"}), 400

    # Decode the base64 image
    image_data = image_data.split(',')[1]  # Remove base64 prefix
    img = Image.open(BytesIO(base64.b64decode(image_data)))
    
    # Save the image
    image_filename = secure_filename(f"{prediction}.jpg")
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
    img.save(image_path)

    # Save prediction to database
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO predictions (image_name, classification) VALUES (?, ?)""",
                   (image_filename, prediction))
    conn.commit()
    conn.close()

    response = {
        "message": "Prediction received and saved successfully",
        "received_prediction": prediction,
        "image_filename": image_filename
    }
    return jsonify(response)


# Route to view predictions saved in the database
@app.route('/predictions')
def view_predictions():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM predictions")
    predictions = cursor.fetchall()
    conn.close()
    return jsonify(predictions)

if __name__ == "__main__":
    app.run(debug=True)
