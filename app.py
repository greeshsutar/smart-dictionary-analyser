from flask import Flask, render_template, request, send_file
import os
from deep_translator import GoogleTranslator
from transformers import pipeline
from gtts import gTTS

app = Flask(__name__)

# Create output directory
if not os.path.exists("output"):
    os.makedirs("output")

audio_path = "output/output.mp3"

# Load summarization model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")


# -----------------------------------------------------------
# HOME PAGE
# -----------------------------------------------------------
@app.route("/")
def home():
    return render_template("home.html")


# -----------------------------------------------------------
# TRANSLATE PAGE
# -----------------------------------------------------------
@app.route("/translate", methods=["GET", "POST"])
def translate():

    translated = ""
    summarized = ""
    original_text = ""
    selected_language = "English"

    if request.method == "POST":
        original_text = request.form["input_text"]
        selected_language = request.form["language"]

        # Language Codes
        lang_map = {
            "English": "en",
            "Hindi": "hi",
            "Marathi": "mr",
            "Kannada": "kn"
        }

        target_code = lang_map[selected_language]

        # Translate
        translated = GoogleTranslator(
            source="auto", target=target_code
        ).translate(original_text)

        # Summarize
        english_text = GoogleTranslator(
            source="auto", target="en"
        ).translate(original_text)

        summary_eng = summarizer(
            english_text,
            max_length=130,
            min_length=25,
            do_sample=False
        )[0]["summary_text"]

        summarized = GoogleTranslator(
            source="en", target=target_code
        ).translate(summary_eng)

        # AUDIO
        tts = gTTS(text=summarized, lang=target_code)
        tts.save(audio_path)

    return render_template(
        "index.html",
        original_text=original_text,
        translated=translated,
        summarized=summarized,
        selected_language=selected_language
    )


# -----------------------------------------------------------
# AUDIO FILE ROUTE
# -----------------------------------------------------------
@app.route("/audio")
def audio():
    if os.path.exists(audio_path):
        return send_file(audio_path, mimetype="audio/mpeg")
    return "No audio file available"


# -----------------------------------------------------------
# ABOUT PAGE
# -----------------------------------------------------------
@app.route("/about")
def about():
    return render_template("about.html")


# -----------------------------------------------------------
# SUPPORT PAGE  (SHOWS THE FORM)
# -----------------------------------------------------------
@app.route("/support", methods=["GET", "POST"])
def support():
    # If GET → show page
    return render_template("support.html")


# -----------------------------------------------------------
# FEEDBACK SUBMISSION ROUTE  (NEW + FIXED)
# -----------------------------------------------------------
@app.route("/submit-feedback", methods=["POST"])
def submit_feedback():
    name = request.form.get("name")
    email = request.form.get("email")
    rating = request.form.get("rating")
    message = request.form.get("message")

    # Print in terminal (optional)
    print("\n---- FEEDBACK SUBMITTED ----")
    print("Name:", name)
    print("Email:", email)
    print("Rating:", rating)
    print("Message:", message)
    print("----------------------------\n")

    # Reload support page with success=True
    return render_template("support.html", success=True)


# -----------------------------------------------------------
# DEVELOPER PAGE
# -----------------------------------------------------------
@app.route("/developer")
def developer():
    return render_template("developer.html")


# -----------------------------------------------------------
# RUN APP
# -----------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
