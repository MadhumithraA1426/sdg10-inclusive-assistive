# sdg10-inclusive-assistive

**AI/ML-Enhanced Summarizer & Audio Tool for Disabled Persons**

Developed in 36 hours for a hackathon, this project empowers people with disabilities to quickly grasp information from text PDFs by providing easy-to-read bullet point summaries and downloadable audio—ensuring accessibility, speed, and archiving.

---

## 💡 Project Motivation

- **Purpose:** Make document content accessible for differently-abled users (especially those with reading or visual difficulties).
- **SDG Contribution:** Supports United Nations SDG 10 (Reduced Inequalities) by enabling access to information without barriers.
- **Hackathon:** Built from scratch in 36 hours, focused on practical accessibility.

---

## 🚀 Features

- **Text PDF Upload:** Easily upload any text-based PDF document.
- **Automatic Summarization:** Uses AI to convert dense content into clear, concise bullet points.
- **Audio Generation:** Instantly produces a clear, downloadable audio summary of the extracted content.
- **Downloadable Summaries & Audio:** Store and retrieve summaries and audio for later use—each user can view/download past uploads.
- **Accessibility First:** Simple interface, large buttons/text, and totally usable by screen readers and keyboard navigation.
- **History:** Lists all previous summaries and generated audios for review and download.

---

## 🖥️ Tech Stack

- **Frontend:** HTML, CSS, JavaScript (vanilla)
- **Backend:** Python (Flask, Flask-CORS)
- **AI/ML:** HuggingFace Transformers (BART for summarization), PyMuPDF (PDF parsing), gTTS or pyttsx3 (Text-to-Speech)
- **Storage:** Local file system for storing summaries and audio files

---

## 📸 Demo Screenshots

- *Upload PDF*  
- *View summary as bullet points*  
- *Listen to or download the generated audio*  
- *See a gallery/history of all your summaries and audio files*

---

## ⚡ Quick Start

### 1. Clone the repository

git clone https://github.com/MadhumithraA1426/sdg10-inclusive-assistive.git
cd sdg10-inclusive-assistive


### 2. Backend Setup

cd backend
python -m venv venv

Activate the virtual environment:
Windows:
venv\Scripts\activate

macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt

python app.py

## 🧩 How It Works

1. **Upload PDF:** User adds a text-based PDF.
2. **Summarization:** The backend extracts text, chunks content for length, then uses an AI model to summarize the content into plain English bullet points.
3. **Audio Generation:** The summary is converted to speech; an MP3 is produced.
4. **Results:** User sees and hears the summary, and can download audio.
5. **History:** All previous summaries (text/audio) are shown for review/downloading.

## 📝 License

This repository is released under the MIT License.
