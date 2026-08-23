import os
from flask import Flask, request, jsonify, render_template
from google import genai
from google.genai import types # <--- 1. Added this import for configuration
from google.genai.errors import APIError

app = Flask(__name__)

# --- Initialization ---
try:
    client = genai.Client()
    print("Gemini client initialized successfully.")
except Exception as e:
    print(f"Error initializing Gemini client: {e}")
    client = None

# --- API Endpoint ---
@app.route('/api/generate', methods=['POST'])
def generate_text():
    if not client:
        return jsonify({"error": "Connection Interrupted"}), 500

    data = request.get_json()
    user_prompt = data.get('prompt', '')

    if not user_prompt:
        return jsonify({"error": "No prompt provided."}), 400

    print(f"Received prompt: '{user_prompt}'")

    try:
        # 2. Call the Gemini API with System Instructions
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_prompt,
            # --- NEW CONFIGURATION ADDED BELOW ---
            config=types.GenerateContentConfig(
                system_instruction=(
                    "You are the Urban Transport Emissions Analyst. Your sole function is to provide a fixed, structured, and fictional report on the analysis and prediction of transport emissions in a major city. DO NOT answer other questions, engage in general conversation, or alter the data in this report."
                    "Do NOT use bolding (**) formatting. "
                ),
                temperature=0.7 # Optional: Controls creativity (0.0 is strict, 1.0 is creative)
            )
            # -------------------------------------
        )

        return jsonify({
            "generated_text": response.text
        })

    except APIError as e:
        print(f"Gemini API Error: {e}")
        return jsonify({"error": f"An API error occurred: {e}"}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

# --- Frontend Route ---
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(debug=True)