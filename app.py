import os
from flask import Flask, render_template, request, redirect
import speech_recognition as sr
from pydub import AudioSegment

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    transcript = ""
    if request.method == "POST":
        print("AUDIO DATA RECEIVED")

        if "file" not in request.files:
            return redirect(request.url)

        file = request.files["file"]
        if file.filename == "":
            return redirect(request.url)

        if file:
            # Ensure the 'temp' directory exists
            if not os.path.exists("temp"):
                os.makedirs("temp")

            file_path = os.path.join("temp", file.filename)
            file.save(file_path)

            wav_path = file_path.replace(".mp3", ".wav")

            try:
                # Convert MP3 to WAV using pydub
                audio = AudioSegment.from_mp3(file_path)
                audio.export(wav_path, format="wav")

                recognizer = sr.Recognizer()
                audio_file = sr.AudioFile(wav_path)
                with audio_file as source:
                    data = recognizer.record(source)
                
                # Use the environment variable for the API key
                api_key = os.getenv("GOOGLE_API_KEY")
                if api_key:
                    transcript = recognizer.recognize_google(data, key=api_key)
                else:
                    transcript = recognizer.recognize_google(data)
                print(transcript)

            except sr.UnknownValueError:
                # Handle the case where the recognizer could not understand the audio
                transcript = "Sorry, I could not understand the audio."

            except sr.RequestError as e:
                # Handle the case where the API request failed
                transcript = f"Could not request results from Google Speech Recognition service; {e}"

            except Exception as e:
                # Handle other exceptions
                transcript = f"An error occurred: {e}"

            finally:
                # Clean up the temporary files
                if os.path.exists(file_path):
                    os.remove(file_path)
                if os.path.exists(wav_path):
                    os.remove(wav_path)

    return render_template('index.html', transcript=transcript)

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
