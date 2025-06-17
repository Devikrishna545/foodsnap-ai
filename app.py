from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from PIL import Image
import os
import io
import torch
from torchvision import transforms, models
from dotenv import load_dotenv
import google.generativeai as genai
from appconfig import FOOD_ANALYSIS_PROMPT, test_secret_key, ALLOWED_EXTENSIONS
import time
from login import login

# --- Config and Setup ---

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Flask app
flask_app = Flask(__name__, template_folder="templates", static_folder="static")
flask_app.secret_key = test_secret_key  # Change this in production

# Register login, logout, signup routes
login(flask_app)

# Pretrained model for food classification
food_model = models.resnet18(pretrained=True)
food_model.eval()
food_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# --- Utility Functions ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_food_image(image_bytes, threshold=0.5):
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    input_tensor = food_transform(image).unsqueeze(0)
    with torch.no_grad():
        output = food_model(input_tensor)
        probabilities = torch.nn.functional.softmax(output[0], dim=0)
        top5_prob, top5_catid = torch.topk(probabilities, 5)
        # For demonstration, treat ImageNet class indices 948-1000 as food (not accurate, just for demo)
        is_food = any(948 <= catid <= 1000 for catid in top5_catid.tolist())
        return is_food or top5_prob[0].item() > threshold

def preprocess_image(image_bytes, max_size_mb=2, target_size=512):
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    width, height = image.size
    if max(width, height) > target_size:
        if width > height:
            new_width = target_size
            new_height = int(target_size * height / width)
        else:
            new_height = target_size
            new_width = int(target_size * width / height)
        image = image.resize((new_width, new_height))
    buf = io.BytesIO()
    quality = 95
    image.save(buf, format='JPEG', quality=quality)
    while buf.tell() > max_size_mb * 1024 * 1024 and quality > 20:
        buf.seek(0)
        buf.truncate()
        quality -= 5
        image.save(buf, format='JPEG', quality=quality)
    return buf.getvalue()

def call_gemini_multimodal(image_bytes): 
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    # Use the correct way to send image data (as a dict with mime_type and data)
    prompt = FOOD_ANALYSIS_PROMPT
    response = model.generate_content(
        [
            prompt,
            {
                "mime_type": "image/jpeg",
                "data": image_bytes
            }
        ],
        stream=False
    )
    try:
        text = response.candidates[0].content.parts[0].text
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end != -1:
            json_str = text[start:end]
            import json
            return json.loads(json_str)
        else:
            return {"error": "Uploaded image is not recognized as food.", "raw_response": text}
    except Exception:
        return {"error": "Failed to parse Gemini response", "raw_response": str(response)}

# --- Flask Endpoints ---
@flask_app.route("/", methods=["GET"])
def flask_index():
    if "user" not in session:
        return redirect(url_for("login_view"))
    return render_template("index.html")

@flask_app.route("/upload/", methods=["POST"])
def flask_upload_image():
    if request.is_json:
        # Simulate upload delay
        time.sleep(1)
        data = request.get_json()
        image_data = data.get("image_data")
        filename = data.get("filename", "uploaded_image.jpg")
        extension = filename.rsplit('.', 1)[-1].lower()
        if not image_data:
            return jsonify({"error": "No image data provided."})
        # Simulate base64 conversion delay
        time.sleep(1)
        # Remove base64 header if present
        if "," in image_data:
            image_data = image_data.split(",")[1]
        import base64
        image_bytes = base64.b64decode(image_data)
        if not allowed_file(f"file.{extension}"):
            return jsonify({"error": "Invalid file type. Only png, jpg, jpeg allowed."})
        if not is_food_image(image_bytes):
            return jsonify({"error": "Uploaded image is not recognized as food."})
        # Save image in static/uploads
        static_upload_dir = os.path.join("static", UPLOAD_DIR)
        os.makedirs(static_upload_dir, exist_ok=True)
        file_location = os.path.join(static_upload_dir, filename)
        with open(file_location, "wb") as buffer:
            buffer.write(image_bytes)
        # Simulate file save delay
        time.sleep(1)
        # Pass the file path to analyze-food
        data = {
            "file_path": file_location,
            "extension": extension
        }
        with flask_app.test_request_context(
            "/analyze-food/",
            method="POST",
            json=data
        ):
            return flask_analyze_food()
    

@flask_app.route("/analyze-food/", methods=["POST"])
def flask_analyze_food():
    if request.is_json:
        # Simulate processing delay
        time.sleep(1)
        data = request.get_json()
        file_path = data.get("file_path")
        extension = data.get("extension", "jpg")
        if not file_path or not os.path.exists(file_path):
            return jsonify({"error": "Image file not found."})
        with open(file_path, "rb") as f:
            image_bytes = f.read()
        if not allowed_file(f"file.{extension}"):
            return jsonify({"error": "Invalid file type. Only png, jpg, jpeg allowed."})
        if not is_food_image(image_bytes):
            return jsonify({"error": "Uploaded image is not recognized as food."})
    else:
        if "file" not in request.files:
            return jsonify({})
        file = request.files["file"]
        if file.filename == "":
            return jsonify({})
        if not allowed_file(file.filename):
            return jsonify({})
        image_bytes = file.read()
        if not is_food_image(image_bytes):
            return jsonify({})
    # Simulate preprocessing delay
    time.sleep(1)
    processed_image = preprocess_image(image_bytes)
    # Simulate LLM call delay
    time.sleep(1)
    result = call_gemini_multimodal(processed_image)
    return jsonify(result)

# --- Run Section ---
if __name__ == "__main__":
    import sys
    if "fastapi" in sys.argv:
        import uvicorn
        uvicorn.run("app:fastapi_app", host="0.0.0.0", port=8000, reload=True)
    else:
        flask_app.run(debug=True)

