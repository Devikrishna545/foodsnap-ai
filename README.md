# FoodSnap AI - Hackathon Project

🎉 **Welcome to the FoodSnap AI Hackathon!** 🎉

## Overview

FoodSnap AI is a web application that leverages deep learning and large language models to analyze food images. Users can upload a photo of their meal, and the app will identify the food items, estimate their calories, and suggest portion sizes. The project demonstrates the integration of computer vision, multimodal LLMs, and a modern web UI.

## Features

- **User Authentication:** Sign up, login, and logout functionality.
- **Modern UI:** Responsive, theme-switchable (light/dark) interface for uploading and analyzing food images.
- **Food Image Validation:** Uses a pretrained ResNet18 model to check if the uploaded image is likely to be food.
- **Image Preprocessing:** Uploaded images are resized and compressed for efficient processing.
- **Multimodal LLM Integration:** Calls Google Gemini's multimodal API to analyze the food image and extract structured information.
- **Results Table:** Displays detected food items, estimated calories, and portion sizes in a clear table, including total calories.
- **Robust Error Handling:** User-friendly error messages for invalid uploads or processing failures.
- **Extensible Architecture:** Modular codebase for easy extension or replacement of components.

## Tech Stack

- **Frontend:** HTML, CSS (theme-light/dark), JavaScript (vanilla, no frameworks), Bootstrap for forms.
- **Backend:** Python, Flask (REST API), PyTorch (torchvision), Google Generative AI (Gemini API), Pillow, python-dotenv.
- **Model:** Pretrained ResNet18 (ImageNet) for food image validation.
- **LLM:** Google Gemini multimodal API for food, calorie, and portion analysis.

## System Architecture

- **MVC Pattern:**  
  - *Model*: Food classifier, preprocessing, and LLM integration in backend.  
  - *View*: Jinja2 HTML templates and CSS for UI.  
  - *Controller*: Flask routes handle user requests and orchestrate processing.

- **Separation of Concerns:**  
  - Configuration (labels, prompts) in `appconfig.py`.  
  - Static files (CSS/JS) and templates in dedicated folders.

- **API Gateway:**  
  - All user interactions go through Flask API endpoints.

- **Internal Service Calls:**  
  - `/upload/` endpoint internally calls `/analyze-food/` for streamlined workflow.

- **Security & Validation:**  
  - File type and content validation on backend.  
  - Only allowed image formats are processed.

## How It Works

1. **User uploads a food image** via the web UI.
2. **Frontend** converts the image to base64 and sends it as JSON to the `/upload/` endpoint.
3. **Backend** decodes and saves the image, validates it as food, and preprocesses it.
4. The backend **calls the Gemini multimodal API** with the image and a prompt.
5. **Gemini LLM** returns a JSON with food items, calories, and portions.
6. **Frontend displays** the results in a table, including a total calories row.

## Usage Instructions

1. **Clone the repository** and install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

2. **Set up your environment variables:**
    - Copy `.env_sample` to `.env` and add your Gemini API key.

3. **Run the Flask app:**
    ```bash
    python app.py
    ```

4. **Open your browser** and go to `http://localhost:5000`.

5. **Sign up or log in**, then upload a food image to analyze.

## Configuration

- **Food labels and prompts** are managed in `appconfig.py`.
- **Allowed image formats:** PNG, JPG, JPEG.
- **Uploads** are saved in `static/uploads/`.

## Extending the Project

- Swap out the food classifier in `app.py` for a more accurate model.
- add a storage  either azure blob storage or S3 bucket due to scalability ,accesibility.
- Update the prompt in `appconfig.py` for different LLM behaviors.
- Add more endpoints or UI features as needed.

## License

This project is for educational and hackathon purposes only.

