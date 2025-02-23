from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from gen_docs import generate_prediction,coordinate,weatherpred,dosepred
import json
import traceback
import os
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image

# Initialize Flask app
app = Flask(__name__)

# Load models
models = {
    "wheat": tf.keras.models.load_model("model/wheat_leaf_disease_model.h5"),
    "rice": tf.keras.models.load_model("model/improved_rice_leaf_disease_model.h5"),
    "maize": tf.keras.models.load_model("model/maize_leaf_disease_model.h5"),
    "tomato": tf.keras.models.load_model("model/tomato_disease_model.h5"),
    "potato": tf.keras.models.load_model("model/potato_disease_model.h5"),
    "pepper": tf.keras.models.load_model("model/pepper_disease_model.h5")  # Added Pepper Model
}

# Class labels for each model
class_labels = {
    "wheat": ['Healthy', 'Septoria', 'Stripe Rust'],
    "rice": ['Blast', 'Blight', 'Tungro'],
    "maize": ['Blight', 'Common Rust', 'Gray Leaf Spot', 'Healthy'],
    "tomato": [
        'Tomato_Bacterial_spot',
        'Tomato_Early_blight',
        'Tomato_Late_blight',
        'Tomato_Leaf_Mold',
        'Tomato_Septoria_leaf_spot',
        'Tomato_Spider_mites_Two_spotted_spider_mite',
        'Tomato_Target_Spot',
        'Tomato_Tomato_YellowLeaf_Curl_Virus',
        'Tomato_Tomato_mosaic_virus',
        'Tomato_healthy'
    ],
    "potato": [
        'Potato__Early_blight',
        'Potato__Late_blight',
        'Potato__healthy'
    ],
    "pepper": [  # Added Pepper Classes
        'Pepper_bell__Bacterial_spot',
        'Pepper_bell__healthy'
    ]
}

# Ensure upload folder exists
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Set upload folder in Flask config
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Image size expected by model
IMG_SIZE = (224, 224)  # Updated to match model's expected input size

# Route for home page
@app.route("/")
def home():
    return render_template("index.html")

def create_leaf_mask(image):
    """Create a mask for the leaf area, excluding the background."""
    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    
    # Define green range for healthy leaf tissue
    lower_green = np.array([25, 20, 20])
    upper_green = np.array([95, 255, 255])
    leaf_mask = cv2.inRange(hsv, lower_green, upper_green)
    
    # Define brown color for diseased areas
    lower_brown = np.array([10, 20, 20])
    upper_brown = np.array([25, 255, 255])
    brown_mask = cv2.inRange(hsv, lower_brown, upper_brown)
    
    # Combine masks
    leaf_mask = cv2.bitwise_or(leaf_mask, brown_mask)
    
    # Morphological transformations
    kernel = np.ones((5,5), np.uint8)
    leaf_mask = cv2.morphologyEx(leaf_mask, cv2.MORPH_CLOSE, kernel)
    leaf_mask = cv2.morphologyEx(leaf_mask, cv2.MORPH_OPEN, kernel)
    
    return leaf_mask

def segment_diseased_regions(image_path):
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    leaf_mask = create_leaf_mask(img)
    
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    
    # Define disease color ranges
    lower_disease1 = np.array([15, 50, 50])
    upper_disease1 = np.array([30, 255, 255])
    lower_disease2 = np.array([0, 0, 0])
    upper_disease2 = np.array([180, 255, 30])
    
    disease_mask1 = cv2.inRange(hsv, lower_disease1, upper_disease1)
    disease_mask2 = cv2.inRange(hsv, lower_disease2, upper_disease2)
    disease_mask = cv2.bitwise_or(disease_mask1, disease_mask2)
    
    kernel = np.ones((3,3), np.uint8)
    disease_mask = cv2.morphologyEx(disease_mask, cv2.MORPH_OPEN, kernel)
    disease_mask = cv2.morphologyEx(disease_mask, cv2.MORPH_CLOSE, kernel)
    
    final_disease_mask = cv2.bitwise_and(disease_mask, leaf_mask)
    
    return final_disease_mask, leaf_mask

def calculate_severity(disease_mask, leaf_mask):
    diseased_pixels = np.sum(disease_mask == 255)
    total_leaf_pixels = np.sum(leaf_mask == 255)
    
    if total_leaf_pixels == 0:
        return 0.0
    
    severity = (diseased_pixels / total_leaf_pixels) * 100
    return min(severity, 100.0)

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files or 'plant' not in request.form:
        return jsonify({"error": "Missing file or plant type"}), 400
    
    file = request.files['file']
    plant = request.form['plant']
    
    if file.filename == '' or plant not in models:
        return jsonify({"error": "Invalid file or plant type"}), 400
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)
    
    try:
        # Load and preprocess the image
        img = image.load_img(file_path, target_size=IMG_SIZE)
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array /= 255.0  # Normalize pixel values

        # Predict disease
        prediction = models[plant].predict(img_array)
        predicted_class = np.argmax(prediction, axis=1)[0]
        disease_name = class_labels[plant][predicted_class]
        
        # Calculate severity
        disease_mask, leaf_mask = segment_diseased_regions(file_path)
        severity = calculate_severity(disease_mask, leaf_mask)
        
        return jsonify({
            "disease": disease_name,
            "severity": round(severity, 2),
            "image_url": f"/{file_path}"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/generate-docs', methods=['POST'])
def generate_docs():
    print("generate_docs function called in Flask")
    
    try:
        data = request.get_json()
        required_keys = {'crop', 'disease', 'longitude', 'latitude'}

        if not required_keys.issubset(data.keys()):
            return jsonify({"error": "Missing required fields."}), 400
        
        crop = data['crop']
        disease = data['disease']
        location = f"Longitude: {data['longitude']}, Latitude: {data['latitude']}"

        response_text = generate_prediction(disease, crop, location)
        
        if response_text:
            return jsonify({"Fertilizers etc": response_text})
        else:
            return jsonify({"error": "Failed to generate prediction"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/weatherprediction', methods=['POST'])
def weatherprediction():
    print("weatherprediction function called in Flask")
    
    try:
        data = request.get_json()
        required_keys = {'crop', 'disease', 'duration', 'location'}

        if not required_keys.issubset(data.keys()):
            return jsonify({"error": "Missing required fields."}), 400
        Location = data['location']
        Crop = data['crop']
        Disease = data['disease']
        Duration = data['duration']
        print(Location)
        response_text = weatherpred(Disease,Crop,Duration,Location)
        
        if response_text:
            return jsonify({"Weather prediction is ": response_text})
        else:
            return jsonify({"error": "Failed to generate prediction"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# @app.route('/doseprediction', methods=['POST'])
# def doseprediction():
#     print("doseprediction function called in Flask")
    
#     try:
#         data = request.get_json()
#         required_keys = {'crop_type', 'growth_stage', 'fertilizer_name', 'plot_size'}

#         if not required_keys.issubset(data.keys()):
#             return jsonify({"error": "Missing required fields."}), 400
        
#         Crop_type = data['crop_type']
#         Growth_stage = data['growth_stage']
#         Fertilizer_name = data['fertilizer_name']
#         Plot_size = data['plot_size']
        
#         response_text = dosepred(Crop_type, Growth_stage, Fertilizer_name, Plot_size)
        
#         if not response_text:
#             return jsonify({"error": "Empty response from dosepred"}), 500
        
#         # Ensure it's valid JSON (clean up text if needed)
#         try:
#             if isinstance(response_text, str):
#                 response_text = response_text.strip()  # Remove extra whitespace/newlines
#                 if response_text.startswith('```json'):
#                     response_text = response_text.replace('```json', '').replace('```', '').strip()
                
#                 response_data = json.loads(response_text)
#             else:
#                 response_data = response_text

#             if not isinstance(response_data, dict):
#                 raise ValueError("Response is not a JSON object")

#         except json.JSONDecodeError as e:
#             print("JSON parsing error:", e)
#             return jsonify({"error": "Invalid JSON format in dosepred response"}), 500
        
#         # Validate expected keys
#         if "fertilizer" in response_data and "quantity" in response_data:
#             return jsonify({"Dose prediction": response_data})
#         else:
#             return jsonify({"error": "Missing expected keys in dosepred response"}), 500

#     except Exception as e:
#         print("Unexpected error:", e)
#         traceback.print_exc()
#         return jsonify({"error": str(e)}), 500
@app.route('/doseprediction', methods=['POST'])
def doseprediction():
    print("doseprediction function called in Flask")
    
    try:
        data = request.get_json()
        required_keys = {'crop_type', 'growth_stage', 'fertilizer_name', 'plot_size'}

        if not required_keys.issubset(data.keys()):
            return jsonify({"error": "Missing required fields."}), 400
        
        Crop_type = data['crop_type']
        Growth_stage = data['growth_stage']
        Fertilizer_name = data['fertilizer_name']
        Plot_size = data['plot_size']
        
        response_text = dosepred(Crop_type, Growth_stage, Fertilizer_name, Plot_size)
        print("Raw response from dosepred:", repr(response_text))  # Log full output
        
        if not response_text:
            return jsonify({"error": "Empty response from dosepred"}), 500
        
        # Ensure AI response is valid JSON
        try:
            if isinstance(response_text, str):
                response_text = response_text.strip()  # Remove whitespace/newlines
                
                # Remove Markdown-style JSON wrappers
                if response_text.startswith('```json'):
                    response_text = response_text.replace('```json', '').replace('```', '').strip()
                
                # Extract JSON content only
                start = response_text.find('{')
                end = response_text.rfind('}')
                if start == -1 or end == -1:
                    raise ValueError("No JSON object found in response")
                
                clean_json = response_text[start:end + 1]
                response_data = json.loads(clean_json)
            else:
                response_data = response_text

            if not isinstance(response_data, dict):
                raise ValueError("Response is not a JSON object")

        except (json.JSONDecodeError, ValueError) as e:
            print("JSON parsing error:", e)
            return jsonify({"error": "Invalid JSON format in dosepred response"}), 500
        
        # Validate expected keys
        if "fertilizer" in response_data and "quantity" in response_data:
            return jsonify({"Dose prediction": response_data})
        else:
            return jsonify({"error": "Missing expected keys in dosepred response"}), 500

    except Exception as e:
        print("Unexpected error:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)