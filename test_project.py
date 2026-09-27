from project import clean_text, normalize_answer, calculate_score, extract_json
import pytest
import warnings
warnings.filterwarnings("ignore")  # Ignore warnings during tests

# -------------------------------
# 1. Tests for clean_text
# -------------------------------


@pytest.mark.parametrize("input_text,expected", [
    ("  Hello   world  ", "Hello world"),
    ("\nHello\t\tworld\n", "Hello world"),
    ("   ", ""),
    ("Line1\nLine2\n\nLine3", "Line1 Line2 Line3")
])
def test_clean_text(input_text, expected):
    assert clean_text(input_text) == expected


# -------------------------------
# 2. Tests for normalize_answer
# -------------------------------
@pytest.mark.parametrize("input_str,expected", [
    ("a", "A"),
    ("B ", "B"),
    (" c", "C"),
    ("d", "D"),
    ("E", ""),           # invalid letter
    ("", ""),            # empty
    ("   ", ""),         # only spaces
    ("Answer: b", "A"),  # matches first letter due to current function
])
def test_normalize_answer(input_str, expected):
    assert normalize_answer(input_str) == expected


# -------------------------------
# 3. Tests for calculate_score
# -------------------------------
@pytest.mark.parametrize("user_answers,correct_answers,expected_score", [
    (['A', 'B', 'C'], ['A', 'B', 'C'], 3),
    (['A', 'B', 'C'], ['A', 'C', 'C'], 2),
    (['A', 'B', 'C'], ['D', 'D', 'D'], 0),
    (['A', 'B'], ['A', 'B', 'C'], 2),  # different lengths, zip truncates
    ([], [], 0)
])
def test_calculate_score(user_answers, correct_answers, expected_score):
    assert calculate_score(user_answers, correct_answers) == expected_score


def test_extract_json_keeps_the_answer_key():
    quiz = extract_json('''[
        {
            "question": "What is 2 + 2?",
            "options": ["A) 3", "B) 4", "C) 5", "D) 6"],
            "answer": "B",
            "explanation": "Two plus two equals four."
        }
    ]''')

    assert quiz == [{
        "question": "What is 2 + 2?",
        "options": ["A) 3", "B) 4", "C) 5", "D) 6"],
        "answer": "B",
        "explanation": "Two plus two equals four.",
    }]


def test_extract_json_rejects_questions_without_complete_feedback():
    quiz = extract_json('''[
        {
            "question": "What is 2 + 2?",
            "options": ["A) 3", "B) 4", "C) 5", "D) 6"]
        }
    ]''')

    assert quiz is None
