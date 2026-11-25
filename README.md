# Final Project by Saima Usman
# 🤖 AI Study Buddy - Your Smart Study Partner

#### Video Demo: https://youtu.be/hLJ6vtoMfrs

#### Live Demo: https://ai-study-buddy.streamlit.app

---

## Description:
AI Study Buddy is your smart virtual study companion powered by OpenAI.
It helps you **chat**, **summarize notes**, and **generate quizzes** — all in one place.

AI Study Buddy is a Streamlit application for chatting about study topics, summarizing notes, and generating customized multiple-choice quizzes.

---

## 🎯 Project Overview

The AI Study Buddy is built with Python and Streamlit, offering a seamless web interface that does not require any technical setup from end users. Users can chat directly with an AI model to ask questions, summarize their uploaded notes (PDF or text), or test their understanding through automatically generated quizzes. The app is designed for accessibility, simplicity, and performance, ensuring a productive and engaging learning experience.

This project combines Streamlit, the OpenAI API, and PDF parsing with PyPDF2.

---

## ⚙️ Features

### 💬 Chat with AI
Ask the AI assistant any study-related question and receive structured, well-formatted answers with headings, bullet points, and explanations. Perfect for clarifying concepts and understanding complex topics.

### 🧾 Summarize Notes
Upload your lecture notes or textbooks in PDF or TXT format, and the app extracts and summarizes key information for quick review.

### 🎯 Quiz Me
Generate quizzes instantly from your notes or on any given topic. The AI creates five multiple-choice questions (A–D options), and once you answer, it checks your responses, calculates your score, and highlights correct and incorrect answers. This feature promotes active recall and self-assessment.

### ✅ Testable Backend
Core functions such as `clean_text()`, `normalize_answer()`, `calculate_score()`, and `extract_json()` are modular and independently testable using **pytest**, ensuring the app’s logic is reliable and maintainable.

### ✅ To hide external library warnings, RUN:
pytest test_project.py -p no:warnings

---

## 🧩 Tech Stack

- **Frontend/UI**: [Streamlit](https://streamlit.io/)
- **AI Backend**: OpenAI (`gpt-4o-mini` default model)
- **PDF Processing**: PyPDF2
- **Language**: Python 3.10+
- **Testing Framework**: pytest
- **Data Handling**: JSON, Regex

---

## 🚀 Installation and Setup Guide

1️⃣ **Clone the Repository**
Open your terminal or command prompt.

git clone https://github.com/Saima-Devops/ai-study-buddy.git
cd ai-study-buddy

2️⃣ **Create a Virtual Environment**
Create an isolated environment for dependencies:
Run: python -m venv venv

Activate the virtual environment:
Windows: venv\Scripts\activate
**If you get a PowerShell security warning, run this first:**
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

macOS/Linux: source venv/bin/activate

3️⃣ **Install Required Dependencies**
Install all the required Python packages using:
pip install -r requirements.txt

4️⃣ **Configure your API key**
Add the following to your local `.streamlit/secrets.toml` or to your deployed app's Streamlit Secrets. Keep the secrets file out of GitHub.

```toml
OPENAI_API_KEY = "your_openai_api_key"
# OPENAI_MODEL = "gpt-4o-mini"
```

5️⃣ **Run the Streamlit App**
Once everything is set up, start the app with:
streamlit run project.py

Wait a few seconds for Streamlit to start the local server.

6️⃣ **Access the Application**
When the server starts, Streamlit will open the app in your default web browser.


7️⃣ **Explore the Features**
💬 **Chat Tab:** Ask study questions and get AI-generated explanations.
🧾 **Summarize Notes Tab:** Upload a .pdf or .txt file and generate summaries.
🎯 **Quiz Me Tab:** Paste your notes, generate AI-based quizzes, and test yourself.


8️⃣ **Run Tests** (Optional) 
Verify that helper functions work correctly using pytest:
Run: pytest -v

All tests in test_project.py should pass successfully.

---

by **Saima Usman** \
Final Project:**CS50’s Introduction to Programming with Python by Harvard University**
