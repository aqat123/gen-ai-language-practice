import json
from typing import Optional
from sqlalchemy.orm import Session
from uuid import uuid4
from app.db.models import User, ContentLog, UserProgress
from app.services.image_client import get_image_client
from app.core.config import settings
from app.services.srs_service import get_due_reviews, add_word_to_srs, update_review
import random

# Conditionally import Vertex AI client
if settings.USE_VERTEX_AI:
    try:
        from app.services.vertex_image_client import get_vertex_image_client
    except ImportError:
        print("Warning: Vertex AI not available. Install google-cloud-aiplatform.")
from app.services.ai_services import get_llm_client, get_checker_service, get_secondary_validator
from app.schemas.vocabulary import FlashcardResponse, VocabularyAnswerRequest, VocabularyAnswerResponse, ValidationMetadata
from datetime import datetime


async def _generate_image_description_prompt(
    word: str,
    definition: str,
    example_sentence: str,
    target_language: str,
    llm
) -> str:
    """
    Generate a descriptive visual prompt for image generation.
    Uses LLM to convert words into concrete visual descriptions.
    """
    # Use LLM to create a detailed visual description
    prompt = f"""Create a visual image description for a vocabulary flashcard.

Word: {word}
Definition: {definition}
Example: {example_sentence}

Generate a detailed visual scene description (max 15 words) that illustrates this word's meaning.

RULES:
- NO text or words in the image
- Describe specific objects, actions, or scenes
- Be concrete and visual, not abstract
- Simple, clear composition
- Appropriate for education

Examples:
"book" → "an open hardcover book on a wooden table"
"run" → "person jogging on a forest trail, side view"
"happy" → "smiling person with arms raised outdoors"

Visual description:"""

    try:
        response = await llm.generate(
            system_prompt="You create concise visual descriptions for image generation.",
            user_prompt=prompt,
            temperature=0.4,
            max_tokens=128
        )

        # Clean up response
        image_prompt = response.strip().strip('"').strip("'").strip('.')

        # Ensure it's not too long or empty
        if 5 <= len(image_prompt) <= 120:
            return image_prompt
    except Exception as e:
        print(f"[WARNING] Image prompt generation failed: {e}")

    # Fallback: create a simple descriptive prompt
    # Remove "to" prefix for verbs, articles, etc.
    clean_def = definition.lower()
    for prefix in ["to ", "a ", "an ", "the "]:
        if clean_def.startswith(prefix):
            clean_def = clean_def[len(prefix):]

    return f"{clean_def}, clear and simple composition"


async def get_next_flashcard(
    user_id: str,
    target_language: str,
    level: Optional[str],
    db: Session
) -> FlashcardResponse:
    """
    Generate a vocabulary flashcard.

    Args:
        user_id: External user ID
        target_language: Target language
        level: Difficulty level
        db: Database session

    Returns:
        FlashcardResponse with word, definition, example, and options
    """
    llm = get_llm_client()
    checker = get_checker_service()
    secondary_validator = get_secondary_validator()

    # Use Vertex AI if enabled, otherwise use legacy client
    if settings.USE_VERTEX_AI and settings.VERTEX_AI_PROJECT_ID:
        imm_client = get_vertex_image_client(
            credentials_path=settings.VERTEX_AI_CREDENTIALS_PATH,
            project_id=settings.VERTEX_AI_PROJECT_ID,
            location=settings.VERTEX_AI_LOCATION
        )
    else:
        imm_client = get_image_client()

    # Find or create user
    # this is what i fixed: was filtering by external_id, so logged-in users were not found
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        user = User(
            external_id=user_id,
            target_language=target_language,
            level=level
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Check for due SRS reviews first
    due_reviews = get_due_reviews(db, user)
    if due_reviews:
        # Return a random due review as a flashcard
        review = random.choice(due_reviews)

        # Generate simple distractor options (generic wrong answers)
        # This avoids LLM calls for reviews and makes them faster
        distractors = [
            "a type of food or drink",
            "a place or location",
            "an action or activity"
        ]

        # Create options with correct answer at random position
        correct_index = random.randint(0, 3)
        options = distractors[:3]
        options.insert(correct_index, review.definition)

        return FlashcardResponse(
            word=review.word,
            definition=review.definition,
            example_sentence=review.example_sentence or "",
            options=options,
            correct_option_index=correct_index,
            image_data=None,
            is_review=True,
            review_id=review.id,
            validation=ValidationMetadata(
                is_validated=True,
                confidence_score=1.0,
                primary_check_passed=True,
                secondary_check_passed=True
            )
        )

    level_info = f" at {level} level" if level else ""

    # Last 20 seen words to avoid repetition
    recent_logs = db.query(ContentLog) \
        .filter(ContentLog.user_id == user.id, ContentLog.module == "vocabulary") \
        .order_by(ContentLog.created_at.desc()) \
        .limit(20) \
        .all()

    # Extract just the words
    seen_words = []
    for log in recent_logs:
        if log.generated_content and isinstance(log.generated_content, dict):
            word = log.generated_content.get("word")
            if word:
                seen_words.append(word)

    exclusions = ", ".join(seen_words)

    prompt = f"""Generate a vocabulary flashcard for learning {target_language}{level_info}

        IMPORTANT: Do NOT use any of the following words: {exclusions}.
        Pick a random, unique word that is different from the ones listed above.
        Please provide SHORT example sentences (MAX 12 words) that clearly illustrate the meaning of the word.

        Respond ONLY with valid JSON in this exact format:
        {{
          "word": "word in {target_language}",
          "definition": "definition in English",
          "example_sentence": "example sentence using the word in {target_language}",
          "options": ["option1", "option2", "option3", "option4"],
          "correct_option_index": 0
        }}

        The options should be 4 English definitions (one correct, three plausible distractors)."""

    # Generate flashcard
    response = await llm.generate(
        system_prompt=f"You are a language learning content creator. Always respond with valid JSON only.",
        user_prompt=prompt,
        temperature=0.7,
        max_tokens=4096 # Return JSON can be large
    )

    # Parse JSON
    cleaned = response.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]

    flashcard_data = json.loads(cleaned.strip())

    # Stage 1: Primary checker - format and basic validation
    checker_result = await checker.check_content(
        module="vocabulary",
        original_instruction="Generate vocabulary flashcard",
        user_input={"target_language": target_language, "level": level},
        generated_content=json.dumps(flashcard_data)
    )

    # If not valid and has suggested fix, try to use it
    if not checker_result["is_valid"] and checker_result["suggested_fix"]:
        try:
            flashcard_data = json.loads(checker_result["suggested_fix"])
        except (json.JSONDecodeError, TypeError, KeyError):
            pass  # Keep original if parsing fails

    # Stage 2: Secondary validation - deep accuracy and quality check
    secondary_validation = await secondary_validator.deep_validate(
        module="vocabulary",
        user_input={"target_language": target_language, "level": level},
        generated_content=json.dumps(flashcard_data),
        primary_validation=checker_result
    )

    # If secondary validator suggests improvement and has high confidence, use it
    if (not secondary_validation["is_approved"] and
        secondary_validation["improved_version"] and
        secondary_validation["confidence_score"] > 0.7):
        try:
            improved_data = json.loads(secondary_validation["improved_version"])
            flashcard_data = improved_data
        except (json.JSONDecodeError, TypeError, KeyError):
            pass  # Keep current version if parsing fails

    word = flashcard_data.get("word", "")
    definition = flashcard_data.get("definition", "")
    example_sentence = flashcard_data.get("example_sentence", "")
    imm_b64 = None

    if word and definition:
        # Generate image with improved prompt
        # Create a visual, descriptive prompt instead of just the word
        image_prompt = await _generate_image_description_prompt(
            word=word,
            definition=definition,
            example_sentence=example_sentence,
            target_language=target_language,
            llm=llm
        )
        print(f"[DEBUG] Attempting to generate image for word '{word}'")
        print(f"[DEBUG] Image prompt: {image_prompt}")
        print(f"[DEBUG] Using Vertex AI: {settings.USE_VERTEX_AI}")
        imm_b64 = await imm_client.generate_safe_image(image_prompt)
        print(f"[DEBUG] Image generated: {imm_b64 is not None}, size: {len(imm_b64) if imm_b64 else 0}")

    # update the field to be seen in the frontend
    flashcard_data["image_data"] = imm_b64

    # Add validation metadata for frontend display
    flashcard_data["validation"] = {
        "is_validated": checker_result["is_valid"] and secondary_validation["is_approved"],
        "confidence_score": secondary_validation.get("confidence_score"),
        "primary_check_passed": checker_result["is_valid"],
        "secondary_check_passed": secondary_validation["is_approved"]
    }

    # Log content with both validation stages
    content_log = ContentLog(
        user_id=user.id,
        module="vocabulary",
        input_payload={"target_language": target_language, "level": level},
        generated_content=flashcard_data,
        checker_result=checker_result,
        secondary_validation=secondary_validation,
        is_validated=checker_result["is_valid"] and secondary_validation["is_approved"]
    )
    db.add(content_log)
    db.commit()

    # Add new word to SRS for future review
    add_word_to_srs(
        db=db,
        user=user,
        word=word,
        definition=definition,
        example_sentence=example_sentence
    )

    return FlashcardResponse(**flashcard_data)


async def submit_vocabulary_answer(
    request: VocabularyAnswerRequest,
    current_user: User,
    db: Session
) -> VocabularyAnswerResponse:
    """
    Submit a vocabulary answer and get feedback.

    Args:
        request: Answer submission request
        current_user: Authenticated user from token
        db: Database session

    Returns:
        VocabularyAnswerResponse with correctness and explanation
    """
    user = current_user

    is_correct = request.selected_option_index == request.correct_option_index

    # If this is an SRS review, update the review
    if request.review_id is not None and request.quality is not None:
        update_review(db, request.review_id, request.quality)

    # Update user progress
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == user.id,
        UserProgress.module == "vocabulary"
    ).first()

    if not progress:
        progress = UserProgress(
            user_id=user.id,
            module="vocabulary",
            total_attempts=1,
            correct_attempts=1 if is_correct else 0
        )
        db.add(progress)
    else:
        progress.total_attempts += 1
        if is_correct:
            progress.correct_attempts += 1

    # Calculate score
    if progress.total_attempts > 0:
        progress.score = (progress.correct_attempts / progress.total_attempts) * 100

    # Update last activity timestamp
    progress.last_activity_at = datetime.utcnow()

    db.commit()

    # Check for achievements
    from app.services.achievements_service import check_and_unlock_achievements
    newly_unlocked = check_and_unlock_achievements(user.id, db)

    # Check if user now meets advancement criteria
    from app.services.progress_service import calculate_advancement_eligibility
    eligibility = calculate_advancement_eligibility(user.id, db)
    if eligibility["eligible"] and not user.can_advance:
        user.can_advance = True
        user.advancement_notified_at = datetime.utcnow()
        db.commit()

    explanation = "Correct!" if is_correct else f"The correct answer was option {request.correct_option_index}."

    return VocabularyAnswerResponse(
        is_correct=is_correct,
        correct_option_index=request.correct_option_index,
        explanation=explanation
    )
