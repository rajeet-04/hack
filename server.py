from flask import Flask, render_template, request, jsonify
import os
from llm import query_rag, send_to_local_server
from db import*

app = Flask(__name__)

# Upload Folder Configuration
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)
    print(file_path)
    process_file(file_path,"chroma")
    # Pass filename as a query parameter if needed
    return render_template("chat.html", filename=file.filename)

# Chat Page Route (GET)
@app.route("/chat")
def chat_page():
    return render_template("chat.html")

# Chat API Route (POST)
@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "").strip()
    
    if not user_input:
        return jsonify({"error": "Empty message received"}), 400
    
    # Use query_rag to get the prompt
    rag_prompt = query_rag(user_input)
    if not rag_prompt:
        return jsonify({"error": "No relevant context found"}), 400

    # Send the prompt to the local server
    response = send_to_local_server(rag_prompt)
    
    if response.status_code == 200:
        response_text = response.json().get('content', '')
        return jsonify({"message": response_text})
    else:
        return jsonify({"error": "Failed to get response from the local server"}), 500

if __name__ == "__main__":
    app.run(host="127.168.29.69", port=6969, debug=False)
