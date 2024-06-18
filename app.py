import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import speech_recognition as sr
from pydub import AudioSegment
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['CONVERTED_FOLDER'] = 'converted'

def text_to_pdf(text, output_file):
    c = canvas.Canvas(output_file, pagesize=A4)
    margin = 50
    max_y = A4[1] - margin
    line_height = 14
    font_name = "Times-Roman"

    lines = text.split('\n')

    if is_wrapped(lines):
        lines = wrap_lines(lines)

    y = max_y
    c.setFont(font_name, 12)

    for line in lines:
        line = line.rstrip()
        if y < margin:
            c.showPage()
            c.setFont(font_name, 12)
            y = max_y
        c.drawString(margin, y, line)
        y -= line_height

    c.save()

def is_wrapped(lines):
    max_length = max(len(line) for line in lines)
    return max_length > 90

def wrap_lines(lines):
    wrapped_lines = []
    for line in lines:
        if len(line) > 90:
            wrapped_lines.extend([line[i:i+90] for i in range(0, len(line), 90)])
        else:
            wrapped_lines.append(line)
    return wrapped_lines

def wav_to_text(wav_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_file) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Speech recognition could not understand the audio"
    except sr.RequestError:
        return "Could not request results from the speech recognition service"

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/text_to_pdf', methods=['GET', 'POST'])
def text_to_pdf_page():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and file.filename.endswith('.txt'):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            with open(file_path, 'r') as f:
                text = f.read()
            output_file = os.path.join(app.config['CONVERTED_FOLDER'], 'converted.pdf')
            text_to_pdf(text, output_file)
            return send_from_directory(app.config['CONVERTED_FOLDER'], 'converted.pdf', as_attachment=True)
    return render_template('text_to_pdf.html')

@app.route('/speech_to_pdf', methods=['GET', 'POST'])
def speech_to_pdf_page():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and file.filename.endswith('.wav'):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            text = wav_to_text(file_path)
            output_file = os.path.join(app.config['CONVERTED_FOLDER'], 'converted.pdf')
            text_to_pdf(text, output_file)
            return send_from_directory(app.config['CONVERTED_FOLDER'], 'converted.pdf', as_attachment=True)
    return render_template('speech_to_pdf.html')

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['CONVERTED_FOLDER'], exist_ok=True)
    app.run(debug=True)
