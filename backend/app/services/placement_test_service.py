"""
Placement test service for generating and scoring language proficiency tests.
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from app.db.models import PlacementTest, User
from app.services.placement_test_questions import get_predefined_question
from app.core.config import settings


def start_placement_test(db: Session, user_id: str, target_language: str) -> PlacementTest:
    """
    Start a new placement test by generating all 18 questions upfront using predefined questions.

    Args:
        db: Database session
        user_id: User ID
        target_language: Target language for the test

    Returns:
        Created PlacementTest object with all questions
    """
    # Generate all 18 questions (6 vocab, 6 grammar, 6 reading)
    questions = []

    # Generate vocabulary questions (1 question per level: A1, A2, B1, B2, C1, C2)
    for level in ["A1", "A2", "B1", "B2", "C1", "C2"]:
        question = _generate_vocab_question(target_language, level)
        questions.append({
            "question_number": len(questions) + 1,
            "section": "vocabulary",
            "difficulty_level": level,
            **question
        })

    # Generate grammar questions (1 question per level)
    for level in ["A1", "A2", "B1", "B2", "C1", "C2"]:
        question = _generate_grammar_question(target_language, level)
        questions.append({
            "question_number": len(questions) + 1,
            "section": "grammar",
            "difficulty_level": level,
            **question
        })

    # Generate reading comprehension questions (1 question per level)
    for level in ["A1", "A2", "B1", "B2", "C1", "C2"]:
        question = _generate_reading_question(target_language, level)
        questions.append({
            "question_number": len(questions) + 1,
            "section": "reading",
            "difficulty_level": level,
            **question
        })

    # Create placement test record
    placement_test = PlacementTest(
        user_id=user_id,
        target_language=target_language,
        questions_data={"questions": questions},
        answers_data={"answers": {}},
        completed=False
    )

    db.add(placement_test)
    db.commit()
    db.refresh(placement_test)

    return placement_test


def _generate_vocab_question(language: str, level: str) -> Dict[str, Any]:
    """
    Get a predefined vocabulary question for a specific CEFR level.

    Args:
        language: Target language
        level: CEFR level (A1-C2)

    Returns:
        Dictionary with question_text, options, and correct_answer
    """
    return get_predefined_question(language, "vocabulary", level)


def _generate_grammar_question(language: str, level: str) -> Dict[str, Any]:
    """
    Get a predefined grammar question for a specific CEFR level.

    Args:
        language: Target language
        level: CEFR level (A1-C2)

    Returns:
        Dictionary with question_text, options, and correct_answer
    """
    return get_predefined_question(language, "grammar", level)


def _generate_reading_question(language: str, level: str) -> Dict[str, Any]:
    """
    Get a predefined reading comprehension question for a specific CEFR level.

    Args:
        language: Target language
        level: CEFR level (A1-C2)

    Returns:
        Dictionary with passage, question_text, options, and correct_answer
    """
    return get_predefined_question(language, "reading", level)


def get_next_question(db: Session, test_id: str) -> Optional[Dict[str, Any]]:
    """
    Get the next unanswered question in the test.

    Args:
        db: Database session
        test_id: Placement test ID

    Returns:
        Next question data or None if all answered
    """
    test = db.query(PlacementTest).filter(PlacementTest.id == test_id).first()
    if not test:
        return None

    questions = test.questions_data.get("questions", [])
    answers = test.answers_data.get("answers", {})

    # Find first unanswered question
    for question in questions:
        q_num = str(question["question_number"])
        if q_num not in answers:
            return {
                "test_id": test_id,
                "question": question,
                "current_question_number": question["question_number"],
                "total_questions": len(questions),
                "has_next": question["question_number"] < len(questions)
            }

    return None


def submit_answer(db: Session, test_id: str, question_number: int, selected_option: int) -> bool:
    """
    Submit an answer for a question.

    Args:
        db: Database session
        test_id: Placement test ID
        question_number: Question number
        selected_option: Selected option index (0-3)

    Returns:
        True if answer submitted successfully, False otherwise
    """
    test = db.query(PlacementTest).filter(PlacementTest.id == test_id).first()
    if not test or test.completed:
        return False

    # Store the answer
    answers = test.answers_data.get("answers", {})
    answers[str(question_number)] = selected_option
    test.answers_data = {"answers": answers}

    # Flag the JSON column as modified so SQLAlchemy detects the change
    flag_modified(test, "answers_data")

    db.commit()
    return True


def calculate_results(db: Session, test_id: str) -> Optional[Dict[str, Any]]:
    """
    Calculate test results and determine CEFR level.

    Args:
        db: Database session
        test_id: Placement test ID

    Returns:
        Dictionary with scores and determined level
    """
    test = db.query(PlacementTest).filter(PlacementTest.id == test_id).first()
    if not test:
        return None

    questions = test.questions_data.get("questions", [])
    answers = test.answers_data.get("answers", {})

    # Calculate section scores
    vocab_correct = 0
    vocab_total = 0
    grammar_correct = 0
    grammar_total = 0
    reading_correct = 0
    reading_total = 0

    for question in questions:
        q_num = str(question["question_number"])
        if q_num not in answers:
            continue

        correct_answer = question.get("correct_answer", 0)
        user_answer = answers[q_num]

        if question["section"] == "vocabulary":
            vocab_total += 1
            if user_answer == correct_answer:
                vocab_correct += 1
        elif question["section"] == "grammar":
            grammar_total += 1
            if user_answer == correct_answer:
                grammar_correct += 1
        elif question["section"] == "reading":
            reading_total += 1
            if user_answer == correct_answer:
                reading_correct += 1

    # Calculate percentages
    vocab_score = (vocab_correct / vocab_total * 100) if vocab_total > 0 else 0
    grammar_score = (grammar_correct / grammar_total * 100) if grammar_total > 0 else 0
    reading_score = (reading_correct / reading_total * 100) if reading_total > 0 else 0

    # Calculate overall score (weighted: vocab 35%, grammar 35%, reading 30%)
    overall_score = (vocab_score * 0.35 + grammar_score * 0.35 + reading_score * 0.30)

    # Determine CEFR level based on overall score
    if overall_score >= 90:
        level = "C2"
    elif overall_score >= 80:
        level = "C1"
    elif overall_score >= 65:
        level = "B2"
    elif overall_score >= 45:
        level = "B1"
    elif overall_score >= 30:
        level = "A2"
    else:
        level = "A1"

    # Update test record
    test.vocabulary_score = vocab_score
    test.grammar_score = grammar_score
    test.reading_score = reading_score
    test.overall_score = overall_score
    test.determined_level = level
    test.completed = True

    # Update user's level and placement test status
    user = db.query(User).filter(User.id == test.user_id).first()
    if user:
        user.level = level
        user.placement_test_completed = True
        user.placement_test_score = overall_score

    db.commit()
    db.refresh(test)

    # Generate recommendations
    recommendations = _generate_recommendations(level, vocab_score, grammar_score, reading_score)

    return {
        "test_id": test_id,
        "overall_score": overall_score,
        "determined_level": level,
        "section_scores": [
            {"section": "vocabulary", "score_percentage": vocab_score, "correct_answers": vocab_correct, "total_questions": vocab_total},
            {"section": "grammar", "score_percentage": grammar_score, "correct_answers": grammar_correct, "total_questions": grammar_total},
            {"section": "reading", "score_percentage": reading_score, "correct_answers": reading_correct, "total_questions": reading_total}
        ],
        "recommendations": recommendations,
        "completed_at": test.test_date
    }


def _generate_recommendations(level: str, vocab_score: float, grammar_score: float, reading_score: float) -> List[str]:
    """
    Generate personalized recommendations based on test results.

    Args:
        level: Determined CEFR level
        vocab_score: Vocabulary section score
        grammar_score: Grammar section score
        reading_score: Reading section score

    Returns:
        List of recommendation strings
    """
    recommendations = [
        f"Your proficiency level is {level}. Great job on completing the placement test!"
    ]

    # Find weakest area
    scores = {
        "vocabulary": vocab_score,
        "grammar": grammar_score,
        "reading comprehension": reading_score
    }
    weakest_area = min(scores, key=scores.get)
    strongest_area = max(scores, key=scores.get)

    if scores[weakest_area] < 50:
        recommendations.append(f"Focus on improving your {weakest_area} skills - this is your weakest area.")

    if scores[strongest_area] > 80:
        recommendations.append(f"Excellent performance in {strongest_area}! Keep up the good work.")

    # Level-specific recommendations
    if level in ["A1", "A2"]:
        recommendations.append("Start with basic vocabulary and simple grammar patterns.")
    elif level in ["B1", "B2"]:
        recommendations.append("Focus on expanding vocabulary and mastering complex grammar structures.")
    else:  # C1, C2
        recommendations.append("Challenge yourself with advanced materials and native content.")

    return recommendations


def get_user_test_history(db: Session, user_id: str) -> List[PlacementTest]:
    """
    Get all placement tests for a user.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        List of PlacementTest objects
    """
    return db.query(PlacementTest).filter(PlacementTest.user_id == user_id).order_by(PlacementTest.test_date.desc()).all()
