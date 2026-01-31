"""
Unit tests for vocabulary service.

Tests:
- Flashcard generation
- Answer submission
- Image description generation
- Progress tracking
"""

import pytest
from unittest.mock import AsyncMock, patch
from app.services.vocabulary import (
    get_next_flashcard,
    submit_vocabulary_answer
)
from app.db.models import User, UserProgress
from app.schemas.vocabulary import VocabularyAnswerRequest


class TestFlashcardGeneration:
    """Test flashcard generation."""
    
    @pytest.mark.asyncio
    async def test_generate_flashcard_returns_valid_data(self, db_session):
        """Test that flashcard has correct structure."""
        user = User(
            username="testuser",
            hashed_password="hash",
            target_language="German",
            level="A1"
        )
        db_session.add(user)
        db_session.commit()
        
        flashcard_json = {
            "word": "Buch",
            "definition": "book",
            "example_sentence": "Ich lese ein Buch",
            "options": ["book", "pen", "table", "chair"],
            "correct_option_index": 0
        }
        
        import json
        with patch('app.services.vocabulary.get_llm_client') as mock_get_llm, \
             patch('app.services.vocabulary.get_checker_service') as mock_get_checker, \
             patch('app.services.vocabulary.get_secondary_validator') as mock_get_validator:
            
            mock_llm = AsyncMock()
            mock_llm.generate = AsyncMock(return_value=f"```json\n{json.dumps(flashcard_json)}\n```")
            mock_llm.close = AsyncMock()
            mock_get_llm.return_value = mock_llm
            
            mock_checker = AsyncMock()
            mock_checker.check_content = AsyncMock(return_value={"is_valid": True, "suggested_fix": None})
            mock_get_checker.return_value = mock_checker
            
            mock_validator = AsyncMock()
            mock_validator.deep_validate = AsyncMock(return_value={
                "is_approved": True,
                "confidence_score": 0.9,
                "improved_version": None
            })
            mock_get_validator.return_value = mock_validator
            
            result = await get_next_flashcard(
                user_id=user.id,
                target_language="German",
                level="A1",
                db=db_session
            )
        
        assert result is not None
        assert result.word is not None
        assert result.definition is not None
        assert len(result.options) == 4


class TestAnswerSubmission:
    """Test vocabulary answer submission."""
    
    @pytest.mark.asyncio
    async def test_correct_answer_updates_progress(self, db_session):
        """Test that correct answer updates progress."""
        user = User(
            username="testuser",
            hashed_password="hash",
            target_language="Spanish",
            level="A2"
        )
        db_session.add(user)
        db_session.commit()
        
        request = VocabularyAnswerRequest(
            flashcard_id="test-id",
            word="casa",
            selected_option_index=0,
            correct_option_index=0
        )
        
        result = await submit_vocabulary_answer(
            request=request,
            current_user=user,
            db=db_session
        )
        
        assert result.is_correct is True
        
        # Check progress
        progress = db_session.query(UserProgress).filter(
            UserProgress.user_id == user.id,
            UserProgress.module == "vocabulary"
        ).first()
        
        assert progress is not None
        assert progress.correct_attempts == 1
    
    @pytest.mark.asyncio
    async def test_incorrect_answer_updates_progress(self, db_session):
        """Test that incorrect answer updates progress."""
        user = User(
            username="testuser",
            hashed_password="hash",
            target_language="French",
            level="B1"
        )
        db_session.add(user)
        db_session.commit()
        
        request = VocabularyAnswerRequest(
            flashcard_id="test-id-2",
            word="maison",
            selected_option_index=1,
            correct_option_index=0
        )
        
        result = await submit_vocabulary_answer(
            request=request,
            current_user=user,
            db=db_session
        )
        
        assert result.is_correct is False
        
        progress = db_session.query(UserProgress).filter(
            UserProgress.user_id == user.id,
            UserProgress.module == "vocabulary"
        ).first()
        
        assert progress is not None
        assert progress.total_attempts == 1
        assert progress.correct_attempts == 0
    
    @pytest.mark.asyncio
    async def test_multiple_answers_accumulate_score(self, db_session):
        """Test multiple answers calculate score correctly."""
        user = User(
            username="testuser",
            hashed_password="hash",
            target_language="Italian",
            level="A1"
        )
        db_session.add(user)
        db_session.commit()
        
        # Submit 4 correct, 1 incorrect
        for i in range(5):
            is_correct = i < 4
            request = VocabularyAnswerRequest(
                flashcard_id=f"test-{i}",
                word=f"word{i}",
                selected_option_index=0 if is_correct else 1,
                correct_option_index=0
            )
            
            await submit_vocabulary_answer(
                request=request,
                current_user=user,
                db=db_session
            )
        
        progress = db_session.query(UserProgress).filter(
            UserProgress.user_id == user.id,
            UserProgress.module == "vocabulary"
        ).first()
        
        assert progress.total_attempts == 5
        assert progress.correct_attempts == 4
        assert progress.score == 80.0  # 4/5 = 80%


class TestImageDescriptionGeneration:
    """Test image description prompt generation."""
    
    @pytest.mark.asyncio
    async def test_generate_image_description_prompt(self, db_session):
        """Test image description generation."""
        from app.services.vocabulary import _generate_image_description_prompt
        
        with patch('app.services.vocabulary.get_llm_client') as mock_get_llm:
            mock_llm = AsyncMock()
            mock_llm.generate = AsyncMock(return_value="a red apple on a white table")
            
            result = await _generate_image_description_prompt(
                word="apple",
                definition="a round fruit",
                example_sentence="I eat an apple",
                target_language="English",
                llm=mock_llm
            )
        
        assert result is not None
        assert isinstance(result, str)


class TestVocabularyServiceEdgeCases:
    """Test edge cases in vocabulary service."""
    
    @pytest.mark.asyncio
    async def test_flashcard_without_topic(self, db_session):
        """Test flashcard generation without specific topic."""
        user = User(
            username="testuser",
            hashed_password="hash",
            target_language="Portuguese",
            level="B2"
        )
        db_session.add(user)
        db_session.commit()
        
        flashcard_json = {
            "word": "livro",
            "definition": "book",
            "example_sentence": "Eu leio um livro",
            "options": ["book", "pen", "table", "door"],
            "correct_option_index": 0
        }
        
        import json
        with patch('app.services.vocabulary.get_llm_client') as mock_get_llm, \
             patch('app.services.vocabulary.get_checker_service') as mock_get_checker, \
             patch('app.services.vocabulary.get_secondary_validator') as mock_get_validator:
            
            mock_llm = AsyncMock()
            mock_llm.generate = AsyncMock(return_value=f"```json\n{json.dumps(flashcard_json)}\n```")
            mock_llm.close = AsyncMock()
            mock_get_llm.return_value = mock_llm
            
            mock_checker = AsyncMock()
            mock_checker.check_content = AsyncMock(return_value={"is_valid": True, "suggested_fix": None})
            mock_get_checker.return_value = mock_checker
            
            mock_validator = AsyncMock()
            mock_validator.deep_validate = AsyncMock(return_value={
                "is_approved": True,
                "confidence_score": 0.85,
                "improved_version": None
            })
            mock_get_validator.return_value = mock_validator
            
            result = await get_next_flashcard(
                user_id=user.id,
                target_language="Portuguese",
                level="B2",
                db=db_session
            )
        
        assert result is not None


class TestVocabularyErrorHandling:
    """Test vocabulary error handling and edge cases."""
    
    @pytest.mark.asyncio
    async def test_checker_suggested_fix_applied(self, db_session):
        """Test that checker suggested fix is applied."""
        user = User(
            username="testuser",
            hashed_password="hash",
            target_language="German"
        )
        db_session.add(user)
        db_session.commit()
        
        original_json = {
            "word": "Bad",
            "definition": "bad definition",
            "example_sentence": "bad example",
            "options": ["a", "b"],
            "correct_option_index": 0
        }
        
        fixed_json = {
            "word": "Good",
            "definition": "good definition",
            "example_sentence": "good example",
            "options": ["a", "b", "c", "d"],
            "correct_option_index": 0
        }
        
        import json
        with patch('app.services.vocabulary.get_llm_client') as mock_get_llm, \
             patch('app.services.vocabulary.get_checker_service') as mock_get_checker, \
             patch('app.services.vocabulary.get_secondary_validator') as mock_get_validator, \
             patch('app.services.vocabulary.get_image_client') as mock_get_image:
            
            mock_llm = AsyncMock()
            mock_llm.generate = AsyncMock(side_effect=[
                f"```json\n{json.dumps(original_json)}\n```",
                "a good visual description"
            ])
            mock_llm.close = AsyncMock()
            mock_get_llm.return_value = mock_llm
            
            mock_checker = AsyncMock()
            mock_checker.check_content = AsyncMock(return_value={
                "is_valid": False,
                "suggested_fix": json.dumps(fixed_json)
            })
            mock_get_checker.return_value = mock_checker
            
            mock_validator = AsyncMock()
            mock_validator.deep_validate = AsyncMock(return_value={
                "is_approved": True,
                "improved_version": None,
                "confidence_score": 0.9
            })
            mock_get_validator.return_value = mock_validator
            
            mock_image = AsyncMock()
            mock_image.generate_safe_image = AsyncMock(return_value="base64imagedata")
            mock_get_image.return_value = mock_image
            
            result = await get_next_flashcard(
                user_id=user.id,
                target_language="German",
                level="A1",
                db=db_session
            )
            
            assert result.word == "Good"
    
    @pytest.mark.asyncio
    async def test_secondary_validator_improvement_applied(self, db_session):
        """Test that secondary validator improvement is applied."""
        user = User(
            username="testuser",
            hashed_password="hash",
            target_language="German"
        )
        db_session.add(user)
        db_session.commit()
        
        original_json = {
            "word": "Original",
            "definition": "original definition",
            "example_sentence": "original example",
            "options": ["a", "b", "c", "d"],
            "correct_option_index": 0
        }
        
        improved_json = {
            "word": "Improved",
            "definition": "improved definition",
            "example_sentence": "improved example",
            "options": ["a", "b", "c", "d"],
            "correct_option_index": 0
        }
        
        import json
        with patch('app.services.vocabulary.get_llm_client') as mock_get_llm, \
             patch('app.services.vocabulary.get_checker_service') as mock_get_checker, \
             patch('app.services.vocabulary.get_secondary_validator') as mock_get_validator, \
             patch('app.services.vocabulary.get_image_client') as mock_get_image:
            
            mock_llm = AsyncMock()
            mock_llm.generate = AsyncMock(side_effect=[
                f"```json\n{json.dumps(original_json)}\n```",
                "visual description"
            ])
            mock_llm.close = AsyncMock()
            mock_get_llm.return_value = mock_llm
            
            mock_checker = AsyncMock()
            mock_checker.check_content = AsyncMock(return_value={
                "is_valid": True,
                "suggested_fix": None
            })
            mock_get_checker.return_value = mock_checker
            
            mock_validator = AsyncMock()
            mock_validator.deep_validate = AsyncMock(return_value={
                "is_approved": False,
                "improved_version": json.dumps(improved_json),
                "confidence_score": 0.8
            })
            mock_get_validator.return_value = mock_validator
            
            mock_image = AsyncMock()
            mock_image.generate_safe_image = AsyncMock(return_value="base64imagedata")
            mock_get_image.return_value = mock_image
            
            result = await get_next_flashcard(
                user_id=user.id,
                target_language="German",
                level="A1",
                db=db_session
            )
            
            assert result.word == "Improved"
    
    @pytest.mark.asyncio
    async def test_image_description_fallback_for_short_response(self):
        """Test fallback when LLM response is too short."""
        from app.services.vocabulary import _generate_image_description_prompt
        
        mock_llm = AsyncMock()
        mock_llm.generate = AsyncMock(return_value="book")  # Too short
        
        result = await _generate_image_description_prompt(
            word="Buch",
            definition="book",
            example_sentence="Ich lese ein Buch",
            target_language="German",
            llm=mock_llm
        )
        
        assert "book" in result
        assert "clear and simple composition" in result
    
    @pytest.mark.asyncio
    async def test_image_description_fallback_on_exception(self):
        """Test fallback when LLM raises exception."""
        from app.services.vocabulary import _generate_image_description_prompt
        
        mock_llm = AsyncMock()
        mock_llm.generate = AsyncMock(side_effect=Exception("API Error"))
        
        result = await _generate_image_description_prompt(
            word="Buch",
            definition="book",
            example_sentence="Ich lese ein Buch",
            target_language="German",
            llm=mock_llm
        )
        
        assert "book" in result
        assert "clear and simple composition" in result

    @pytest.mark.asyncio
    async def test_image_description_strips_prefixes(self):
        """Test that image description strips common prefixes from definition."""
        from app.services.vocabulary import _generate_image_description_prompt
        
        mock_llm = AsyncMock()
        mock_llm.generate = AsyncMock(return_value="x")  # Too short (< 5 chars), will use fallback
        
        result = await _generate_image_description_prompt(
            word="run",
            definition="to run",
            example_sentence="I run every day",
            target_language="English",
            llm=mock_llm
        )
        
        # Should strip "to " prefix
        assert "run, clear and simple composition" in result
        
    @pytest.mark.asyncio
    async def test_image_description_strips_article_prefixes(self):
        """Test that image description strips article prefixes."""
        from app.services.vocabulary import _generate_image_description_prompt
        
        mock_llm = AsyncMock()
        mock_llm.generate = AsyncMock(return_value="x")  # Too short
        
        result = await _generate_image_description_prompt(
            word="apple",
            definition="an apple",
            example_sentence="I eat an apple",
            target_language="English",
            llm=mock_llm
        )
        
        # Should strip "an " prefix
        assert "apple, clear and simple composition" in result
    
    @pytest.mark.asyncio
    async def test_image_description_with_the_prefix(self):
        """Test stripping 'the' prefix from definition."""
        from app.services.vocabulary import _generate_image_description_prompt
        
        mock_llm = AsyncMock()
        mock_llm.generate = AsyncMock(return_value="ab")  # Too short
        
        result = await _generate_image_description_prompt(
            word="car",
            definition="the car",
            example_sentence="I drive the car",
            target_language="English",
            llm=mock_llm
        )
        
        assert "car, clear and simple composition" in result
    
    @pytest.mark.asyncio
    async def test_image_description_successful_generation(self):
        """Test successful LLM generation of description."""
        from app.services.vocabulary import _generate_image_description_prompt
        
        mock_llm = AsyncMock()
        mock_llm.generate = AsyncMock(return_value="A friendly golden retriever playing in a park")
        
        result = await _generate_image_description_prompt(
            word="dog",
            definition="a domestic animal",
            example_sentence="The dog barks",
            target_language="English",
            llm=mock_llm
        )
        
        # Should use LLM result since it's between 5-120 chars
        assert "golden retriever" in result
        assert "park" in result
    
    @pytest.mark.asyncio
    async def test_image_description_too_long_uses_fallback(self):
        """Test that very long descriptions use fallback."""
        from app.services.vocabulary import _generate_image_description_prompt
        
        mock_llm = AsyncMock()
        long_description = "a" * 150  # More than 120 chars
        mock_llm.generate = AsyncMock(return_value=long_description)
        
        result = await _generate_image_description_prompt(
            word="elephant",
            definition="large mammal",
            example_sentence="The elephant is big",
            target_language="English",
            llm=mock_llm
        )
        
        # Should use fallback
        assert "large mammal" in result
        assert "clear and simple composition" in result
