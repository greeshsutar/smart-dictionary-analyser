from flask import Flask, render_template, request, send_file
import os
from deep_translator import GoogleTranslator
from gtts import gTTS
from werkzeug.utils import secure_filename
import PyPDF2

app = Flask(__name__)

# -------------------- FOLDERS --------------------
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

audio_path = os.path.join(OUTPUT_FOLDER, "output.mp3")

# -------------------- CONFIG --------------------
ALLOWED_EXTENSIONS = {"txt", "pdf"}

# -------------------- HELPERS --------------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_file(filepath):
    if filepath.endswith(".txt"):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    if filepath.endswith(".pdf"):
        text = ""
        with open(filepath, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
        return text

    return ""


# -------------------- ROUTES --------------------
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/translate", methods=["GET", "POST"])
def translate():

    translated = ""
    summarized = ""
    original_text = ""
    selected_language = "English"

    if request.method == "POST":
        selected_language = request.form.get("language")

        lang_map = {
            "English": "en",
            "Hindi": "hi",
            "Marathi": "mr",
            "Kannada": "kn"
        }

        target_code = lang_map[selected_language]

        # -------- TEXT OR FILE INPUT --------
        text_input = request.form.get("input_text", "").strip()
        file = request.files.get("file")

        if file and file.filename != "" and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            original_text = extract_text_from_file(filepath)
        else:
            original_text = text_input

        if original_text:
            # -------- TRANSLATION --------
            translated = GoogleTranslator(
                source="auto", target=target_code
            ).translate(original_text)

            # -------- CLOUD-SAFE SUMMARY --------
            english_text = GoogleTranslator(
                source="auto", target="en"
            ).translate(original_text)

            # Deployment optimization (full AI model used in local version)
            summary_eng = english_text[:300]

            summarized = GoogleTranslator(
                source="en", target=target_code
            ).translate(summary_eng)

            # -------- AUDIO --------
            tts = gTTS(text=summarized, lang=target_code)
            tts.save(audio_path)

    return render_template(
        "index.html",
        original_text=original_text,
        translated=translated,
        summarized=summarized,
        selected_language=selected_language
    )


@app.route("/audio")
def audio():
    if os.path.exists(audio_path):
        return send_file(audio_path, mimetype="audio/mpeg")
    return "No audio file available"


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/support", methods=["GET", "POST"])
def support():
    return render_template("support.html")


@app.route("/submit-feedback", methods=["POST"])
def submit_feedback():
    return render_template("support.html", success=True)


@app.route("/developer")
def developer():
    return render_template("developer.html")


# -------------------- RUN APP --------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
