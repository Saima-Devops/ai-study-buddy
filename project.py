import streamlit as st
import streamlit.components.v1 as components
from PyPDF2 import PdfReader
import json
import re
import time
from pathlib import Path
from fpdf import FPDF
from fpdf.enums import WrapMode, XPos, YPos
import requests

# -------------------------------
# Helper Functions (UNCHANGED)
# -------------------------------

def clean_text(text: str) -> str:
    return re.sub(r'\s+', ' ', text.strip())


def normalize_answer(answer: str) -> str:
    if not answer:
        return ""
    match = re.match(r'([A-Da-d])', answer.strip())
    return match.group(1).upper() if match else ""


def calculate_score(user_answers: list, correct_answers: list) -> int:
    return sum(ua == ca for ua, ca in zip(user_answers, correct_answers))


def limit_summary(text: str, max_words: int = 100) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]).rstrip(".,;:") + "..."


def clean_pdf_text(text: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"(?m)^\s*#{1,6}\s*", "", text)
    text = re.sub(r"(?m)^\s*[-*+]\s+", "- ", text)
    return re.sub(r"[*_`]", "", text)


def clean_ai_output(text: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"(?m)^\s*#{1,6}\s*", "", text)
    text = re.sub(r"(?m)^\s*[-*+]\s+", "- ", text)
    text = re.sub(r"[*_`~]", "", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def save_chat_response_as_pdf(text: str):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    for raw_line in text.splitlines():
        line = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", raw_line)
        line = line.encode("ascii", "ignore").decode()
        heading = re.match(r"^\s*(#{1,6})\s+(.+)$", line)
        bullet = re.match(r"^\s*[-*+]\s+(.+)$", line)

        if heading:
            level = len(heading.group(1))
            pdf.set_font("Arial", "B", max(12, 20 - level * 2))
            content = re.sub(r"[*_`]", "", heading.group(2))
            height = 9
        elif bullet:
            pdf.set_font("Arial", size=12)
            content = "- " + re.sub(r"[*_`]", "", bullet.group(1))
            height = 7
        else:
            pdf.set_font("Arial", size=12)
            content = re.sub(r"[*_`]", "", line) or " "
            height = 7

        pdf.multi_cell(
            0,
            height,
            content,
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
            wrapmode=WrapMode.CHAR,
        )

    return bytes(pdf.output())


def render_copy_button(text: str, button_id: str):
    safe_text = json.dumps(text).replace("</", "<\\/")
    safe_id = json.dumps(button_id)
    components.html(
        f"""
        <style>
        body {{ margin: 0; overflow: hidden; }}
        .copy-button {{
            background: rgb(255, 255, 255);
            border: 1px solid rgba(49, 51, 63, 0.2);
            border-radius: 0.5rem;
            color: rgb(49, 51, 63);
            cursor: pointer;
            font-family: "Source Sans Pro", sans-serif;
            font-size: 0.875rem;
            font-weight: 400;
            height: 2.5rem;
            padding: 0 0.75rem;
        }}
        .copy-button:hover {{ border-color: rgb(255, 75, 75); color: rgb(255, 75, 75); }}
        </style>
        <button id={safe_id} class="copy-button">
            Copy response
        </button>
        <span id="status" style="margin-left: 8px;"></span>
        <script>
            const text = {safe_text};
            const button = document.getElementById({safe_id});
            const status = document.getElementById("status");

            button.addEventListener("click", async () => {{
                try {{
                    await navigator.clipboard.writeText(text);
                }} catch (error) {{
                    const field = document.createElement("textarea");
                    field.value = text;
                    document.body.appendChild(field);
                    field.select();
                    document.execCommand("copy");
                    field.remove();
                }}
                status.textContent = "Copied";
            }});
        </script>
        """,
        height=54,
    )


def render_robot_avatar(container):
    container.markdown("**:material/smart_toy:**")


def render_assistant_message(text: str, copy_button_id: str | None = None):
    avatar_column, content_column = st.columns([1, 11], vertical_alignment="top")
    render_robot_avatar(avatar_column)
    with content_column:
        display_text = clean_ai_output(text)
        st.markdown(f"**Study Buddy says:**\n\n{display_text}")
        if copy_button_id:
            render_copy_button(display_text, copy_button_id)
            st.download_button(
                "Download response",
                save_chat_response_as_pdf(text),
                "ai-response.pdf",
                "application/pdf",
                key=f"download-{copy_button_id}",
            )


def show_confetti():
    colors = ["#f43f5e", "#f59e0b", "#10b981", "#3b82f6", "#8b5cf6"]
    pieces = "".join(
        f'<span class="confetti-piece" style="left:{(index * 13) % 100}vw; '
        f'background:{colors[index % len(colors)]}; animation-delay:{index * 0.04}s;"></span>'
        for index in range(48)
    )
    st.markdown(
        f"""
        <style>
        .confetti-overlay {{ inset: 0; pointer-events: none; position: fixed; z-index: 9999; }}
        .confetti-piece {{ animation: confetti-fall 2.4s ease-out forwards; height: 10px; position: absolute; top: -12px; width: 6px; }}
        @keyframes confetti-fall {{ to {{ opacity: 0; transform: translateY(105vh) rotate(540deg); }} }}
        @media (prefers-reduced-motion: reduce) {{ .confetti-piece {{ animation: none; display: none; }} }}
        </style>
        <div class="confetti-overlay">{pieces}</div>
        """,
        unsafe_allow_html=True,
    )


def render_quiz_results(quiz, user_answers, score, celebrate=False):
    total = len(quiz)
    score_column, correct_column, review_column = st.columns(3)
    score_column.metric("Score", f"{score}/{total}")
    correct_column.metric("Correct", score)
    review_column.metric("To Review", total - score)

    if score == total:
        st.success("Perfect score! You answered every question correctly. 💪 🏆")
        if celebrate:
            show_confetti()
    elif score >= total * 0.8:
        st.success("Excellent work! Strong score - keep it up. 💪 🏆")
    elif score >= total * 0.6:
        st.info("Good progress. Review the notes below and you will be even stronger next time. 💪")
    else:
        st.warning("Keep practicing - the review below explains every answer. 💪")

    st.subheader("Answer Review")
    for index, (question, user_answer) in enumerate(zip(quiz, user_answers), start=1):
        correct_answer = question["answer"]
        is_correct = user_answer == correct_answer
        status = "Correct" if is_correct else "Needs review"

        with st.expander(f"Q{index}. {status}", expanded=True):
            st.write(question["question"])
            st.write(f"Your answer: {user_answer or 'No answer selected'}")
            st.write(f"Correct answer: {correct_answer}")
            st.write(f"Why: {question['explanation']}")


def save_text_as_pdf(text: str):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    safe_text = clean_pdf_text(text).encode("ascii", "ignore").decode()

    for line in safe_text.split("\n"):
        pdf.multi_cell(
            0,
            8,
            line or " ",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
            wrapmode=WrapMode.CHAR,
        )

    return bytes(pdf.output())


# -------------------------------
# PDF Reader
# -------------------------------

def read_pdf(file):
    pdf = PdfReader(file)
    text = ""
    for page in pdf.pages:
        text += page.extract_text() or ""
    return text


# -------------------------------
# SAFE JSON PARSER
# -------------------------------

def extract_json(text):
    try:
        if not text:
            return None

        match = re.search(r'\[.*\]', text, re.DOTALL)
        if not match:
            return None

        raw = match.group(0)
        raw = raw.replace("'", '"')
        raw = re.sub(r",\s*}", "}", raw)
        raw = re.sub(r",\s*]", "]", raw)

        data = json.loads(raw)

        if isinstance(data, list):
            clean = []
            for item in data:
                if isinstance(item, dict):
                    q = item.get("question")
                    o = item.get("options")
                    answer = normalize_answer(str(item.get("answer", "")))
                    explanation = item.get("explanation")
                    if q and isinstance(o, list) and len(o) == 4 and answer and explanation:
                        clean.append({
                            "question": q,
                            "options": o,
                            "answer": answer,
                            "explanation": explanation,
                        })
            return clean or None

        return None

    except:
        return None


# -------------------------------
# MULTI-API FALLBACK SYSTEM
# -------------------------------

def call_ai(prompt: str) -> str:
    errors = []

    # ---------------- GEMINI ----------------
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if api_key:
        try:
            from google import genai

            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model=st.secrets.get("GEMINI_MODEL", "gemini-2.5-flash"),
                contents=prompt
            )
            if response.text:
                return response.text
            errors.append("Gemini returned an empty response")
        except Exception as error:
            errors.append(f"Gemini failed ({type(error).__name__})")
    else:
        errors.append("Gemini API key is not configured")

    # ---------------- DEEPSEEK ----------------
    deepseek_key = st.secrets.get("DEEPSEEK_API_KEY", "")
    if deepseek_key:
        try:
            import openai

            client = openai.OpenAI(
                api_key=deepseek_key,
                base_url="https://api.deepseek.com",
            )
            response = client.chat.completions.create(
                model=st.secrets.get("DEEPSEEK_MODEL", "deepseek-flash"),
                messages=[{"role": "user", "content": prompt}],
            )

            if response.choices and response.choices[0].message.content:
                return response.choices[0].message.content
            errors.append("DeepSeek returned an empty response")
        except Exception as error:
            errors.append(f"DeepSeek failed ({type(error).__name__})")

    # ---------------- OPENAI (OPTIONAL) ----------------
    api_key = st.secrets.get("OPENAI_API_KEY", "")
    if api_key:
        try:
            import openai

            client = openai.OpenAI(api_key=api_key)

            res = client.chat.completions.create(
                model=st.secrets.get("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[{"role": "user", "content": prompt}]
            )

            if res.choices and res.choices[0].message.content:
                return res.choices[0].message.content
            errors.append("OpenAI returned an empty response")
        except Exception as error:
            errors.append(f"OpenAI failed ({type(error).__name__})")

    return "⚠️ No AI service could complete this request. " + " ".join(errors)


# -------------------------------
# MAIN APP (DO NOT TOUCH UI)
# -------------------------------

def main():
    st.set_page_config(page_title="AI Study Buddy", page_icon="📘", layout="wide")

    logo_path = Path(__file__).parent / "assets" / "logo.png"
    if logo_path.exists():
        st.sidebar.image(str(logo_path), width=140)
    st.sidebar.title("📘 AI Study Buddy")
    page = st.sidebar.radio("Go to:", ["💬 Chat", "🧾 Summarize Notes", "🎯 Quiz Me"])
    st.sidebar.divider()
    st.sidebar.markdown(
        "<div style='color: rgba(49, 51, 63, 0.55); font-size: 0.72rem; line-height: 1.45;'>"
        "All Rights Reserved.<br>Created by Saima Usman for Harvard University’s CS50 Capstone."
        "</div>",
        unsafe_allow_html=True,
    )

    # ---------------- CHAT ----------------
    if page == "💬 Chat":
        st.title("💬 Chat with AI Study Buddy")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []

        for index, msg in enumerate(st.session_state.chat_history):
            if msg["role"] == "assistant":
                render_assistant_message(msg["content"], f"copy-history-{index}")
            else:
                st.markdown(f"**🧑 You:** {msg['content']}")

        user_input = st.chat_input("Ask something...")

        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            st.markdown(f"**🧑 You:** {user_input}")

            thinking_avatar_column, thinking_content = st.columns([1, 11], vertical_alignment="top")
            thinking_avatar = thinking_avatar_column.empty()
            render_robot_avatar(thinking_avatar)
            placeholder = thinking_content.empty()
            for _ in range(3):
                placeholder.markdown("AI is thinking...")
                time.sleep(0.2)

            response = call_ai(user_input)

            placeholder.empty()
            thinking_avatar.empty()
            render_assistant_message(response, "copy-latest-response")

            st.session_state.chat_history.append({"role": "assistant", "content": response})

    # ---------------- SUMMARIZE ----------------
    elif page == "🧾 Summarize Notes":
        st.title("🧾 Summarize Notes")

        file = st.file_uploader("Upload PDF or TXT", type=["pdf", "txt"])

        if file:
            text = read_pdf(file) if file.type == "application/pdf" else file.read().decode()
            text = clean_text(text)

            st.text_area("Extracted Text", text, height=300)

            if st.button("✨ Summarize"):
                summary = call_ai(
                    "Summarize in at most 5 short bullet points and 100 words total. "
                    "Use plain text with no Markdown formatting.\n\n" + text
                )
                summary = limit_summary(summary)
                clean_summary = clean_ai_output(summary)

                st.markdown(clean_summary)

                st.download_button(
                    "💾 Download Summary PDF",
                    save_chat_response_as_pdf(summary),
                    "summary.pdf"
                )

    # ---------------- QUIZ (FIXED + STABLE) ----------------
    elif page == "🎯 Quiz Me":
        st.title("🎯 Quiz Generator")

        quiz_file = st.file_uploader("Upload PDF or TXT notes", type=["pdf", "txt"], key="quiz_file")
        pasted_notes = st.text_area("Paste notes here:", height=300)

        if quiz_file:
            if quiz_file.type == "application/pdf":
                quiz_file.seek(0)
                notes = clean_text(read_pdf(quiz_file))
            else:
                notes = clean_text(quiz_file.getvalue().decode(errors="replace"))
            st.text_area("Uploaded Notes", notes, height=220, disabled=True)
        else:
            notes = pasted_notes

        if st.button("Generate Quiz") and notes:

            prompt = f"""
Generate 5 MCQs in STRICT JSON format only.

FORMAT:
[
  {{
    "question": "...",
    "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
    "answer": "A",
    "explanation": "One short sentence explaining why the answer is correct."
  }}
]

Notes:
{notes}
"""

            quiz = None

            for _ in range(3):
                response = call_ai(prompt)
                quiz = extract_json(response)
                if quiz:
                    break

            if quiz:
                st.session_state.quiz = quiz
                st.session_state.answers = [""] * len(quiz)
                st.session_state.pop("quiz_result", None)
                st.session_state.pop("show_confetti", None)
                for i in range(len(quiz)):
                    st.session_state.pop(f"q{i}", None)
                st.success("Quiz generated successfully!")
            else:
                st.error("Quiz generation failed. Try simpler notes.")

        if "quiz" in st.session_state:

            for i, q in enumerate(st.session_state.quiz):

                question = q.get("question", "Question missing")
                options = q.get("options", ["A", "B", "C", "D"])

                st.markdown(f"**Q{i + 1}.** {question}")

                st.session_state.answers[i] = st.radio(
                    f"Answer for question {i + 1}",
                    options,
                    key=f"q{i}",
                    label_visibility="collapsed",
                )

            if st.button("Submit Quiz"):
                correct = [q.get("answer", "") for q in st.session_state.quiz]
                explanations = [q.get("explanation", "") for q in st.session_state.quiz]
                if not all(correct) or not all(explanations):
                    st.error("This quiz has no complete answer key. Generate a new quiz and try again.")
                else:
                    user = [normalize_answer(a) for a in st.session_state.answers]
                    score = calculate_score(user, correct)
                    st.session_state.quiz_result = {
                        "score": score,
                        "user_answers": user,
                    }
                    st.session_state.show_confetti = score == len(correct)

            if "quiz_result" in st.session_state:
                result = st.session_state.quiz_result
                celebrate = st.session_state.pop("show_confetti", False)
                render_quiz_results(
                    st.session_state.quiz,
                    result["user_answers"],
                    result["score"],
                    celebrate,
                )


# -------------------------------
# RUN APP
# -------------------------------

if __name__ == "__main__":
    main()
