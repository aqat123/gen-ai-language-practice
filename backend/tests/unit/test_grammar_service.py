"""
Unit tests for grammar service.

Tests:
- Grammar question generation
- Answer validation
- Progress tracking
"""

import pytest
from unittest.mock import AsyncMock, patch
from app.services.grammar import (
    get_grammar_question,
    submit_grammar_answer
)
from app.db.models import User, UserProgress
from app.schemas.grammar import GrammarAnswerRequest


class TestGrammarQuestionGeneration:
    """Test grammar question generation."""
    
    @pytest.mark.asyncio
    async def test_generate_grammar_question_returns_valid_structure(self, db_session):
        """Test that grammar question has correct structure."""
        user = User(
            username="testuser",
            hashed_password="hash",
            target_language="Spanish",
            level="A1"
        )
        db_session.add(user)
        db_session.commit()
        
        question_json = {
            "question_text": "Choose the correct verb form",
            "options": ["es", "son", "está", "están"],
            "correct_option_index": 0,
            "explanation": "Use 'es' for singular"
        }
        
        import json
        with patch('app.services.grammar.get_llm_client') as mock_get_llm, \
             patch('app.services.grammar.get_checker_service') as mock_get_checker, \
             patch('app.services.grammar.get_secondary_validator') as mock_get_validator:
            
            mock_llm = AsyncMock()
            mock_llm.generate = AsyncMock(return_value=f"```json\n{json.dumps(question_json)}\n```")
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
            
            result = await get_grammar_question(
                user_id=user.id,
                target_language="Spanish",
                level="A1",
                topic=None,
                db=db_session
            )
        
        assert result is not None
        assert result.question_text is not None
        assert len(result.options) == 4
        assert result.correct_option_index is not None
    
    @pytest.mark.asyncio
    async def test_grammar_question_with_specific_topic(self, db_session):
        """Test generating question for specific grammar topic."""
        user = User(
            username="testuser",
            hashed_password="hash",
            target_language="French",
            level="B1"
        )
        db_session.add(user)
        db_session.commit()
        
        question_json = {
            "question_text": "Select the correct past tense",
            "options": ["ai mangé", "mange", "mangeais", "mangerai"],
            "correct_option_index": 0,
            "explanation": "Passé composé for completed action"
        }
        
        import json
        with patch('app.services.grammar.get_llm_client') as mock_get_llm, \
             patch('app.services.grammar.get_checker_service') as mock_get_checker, \
             patch('app.services.grammar.get_secondary_validator') as mock_get_validator:
            
            mock_llm = AsyncMock()
            mock_llm.generate = AsyncMock(return_value=f"```json\n{json.dumps(question_json)}\n```")
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
            
            result = await get_grammar_question(
                user_id=user.id,
                target_language="French",
                level="B1",
                topic="past tense",
                db=db_session
            )
        
        assert result is not None
        assert hasattr(result, 'question_id')


class TestGrammarAnswerSubmission:
    """Test grammar answer submission."""
    
    @pytest.mark.asyncio
    async def test_correct_answer_updates_progress(self, db_session):
        """Test that correct answer updates progress."""
        user = User(
            username="testuser",
            hashed_password="hash",
            target_language="German",
            level="A2"
        )
        db_session.add(user)
        db_session.commit()
        
        request = GrammarAnswerRequest(
            question_id="test-123",
            selected_option_index=1,
            correct_option_index=1,
            explanation="Correct!"
        )
        
        result = await submit_grammar_answer(
            request=request,
            current_user=user,
            db=db_session
        )
        
        assert result.is_correct is True
        
        # Check progress was created
        progress = db_session.query(UserProgress).filter(
            UserProgress.user_id == user.id,
            UserProgress.module == "grammar"
        ).first()
        
        assert progress is not None
        assert progress.correct_attempts == 1
    
    @pytest.mark.asyncio
    async def test_incorrect_answer_updates_progress(self, db_session):
        """Test that incorrect answer updates progress."""
        user = User(
            username="testuser",
            hashed_password="hash",
            target_language="Italian",
            level="A1"
        )
        db_session.add(user)
        db_session.commit()
        
        request = GrammarAnswerRequest(
            question_id="test-456",
            selected_option_index=0,
            correct_option_index=2,
            explanation="Wrong answer"
        )
        
        result = await submit_grammar_answer(
            request=request,
            current_user=user,
            db=db_session
        )
        
        assert result.is_correct is False
        
        progress = db_session.query(UserProgress).filter(
            UserProgress.user_id == user.id,
            UserProgress.module == "grammar"
        ).first()
        
        assert progress is not None
        assert progress.total_attempts == 1
        assert progress.correct_attempts == 0
    
    @pytest.mark.asyncio
    async def test_multiple_answers_calculate_score_correctly(self, db_session):
        """Test that multiple answers calculate score."""
        user = User(
            username="testuser",
            hashed_password="hash",
            target_language="Portuguese",
            level="B2"
        )
        db_session.add(user)
        db_session.commit()
        
        # Submit 3 correct, 2 incorrect
        for i in range(5):
            is_correct = i < 3
            request = GrammarAnswerRequest(
                question_id=f"test-{i}",
                selected_option_index=0 if is_correct else 1,
                correct_option_index=0,
                explanation="Test"
            )
            
            await submit_grammar_answer(
                request=request,
                current_user=user,
                db=db_session
            )
        
        progress = db_session.query(UserProgress).filter(
            UserProgress.user_id == user.id,
            UserProgress.module == "grammar"
        ).first()
        
        assert progress.total_attempts == 5
        assert progress.correct_attempts == 3
        assert progress.score == 60.0  # 3/5 = 60%


class TestGrammarServiceEdgeCases:
    """Test edge cases in grammar service."""
    
    @pytest.mark.asyncio
    async def test_question_without_level_uses_default(self, db_session):
        """Test question generation without level."""
        user = User(
            username="testuser",
            hashed_password="hash",
            target_language="Japanese",
            level="A1"
        )
        db_session.add(user)
        db_session.commit()
        
        question_json = {
            "question_text": "Test question",
            "options": ["a", "b", "c", "d"],
            "correct_option_index": 0,
            "explanation": "Test"
        }
        
        import json
        with patch('app.services.grammar.get_llm_client') as mock_get_llm, \
             patch('app.services.grammar.get_checker_service') as mock_get_checker, \
             patch('app.services.grammar.get_secondary_validator') as mock_get_validator:
            
            mock_llm = AsyncMock()
            mock_llm.generate = AsyncMock(return_value=f"```json\n{json.dumps(question_json)}\n```")
            mock_llm.close = AsyncMock()
            mock_get_llm.return_value = mock_llm
            
            mock_checker = AsyncMock()
            mock_checker.check_content = AsyncMock(return_value={"is_valid": True, "suggested_fix": None})
            mock_get_checker.return_value = mock_checker
            
            mock_validator = AsyncMock()
            mock_validator.deep_validate = AsyncMock(return_value={
                "is_approved": True,
                "confidence_score": 0.8,
                "improved_version": None
            })
            mock_get_validator.return_value = mock_validator
            
            result = await get_grammar_question(
                user_id=user.id,
                target_language="Japanese",
                level=None,
                topic=None,
                db=db_session
            )
        
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_invalid_json_raises_error(self, db_session):
        """Test handling of invalid JSON from LLM."""
        user = User(
            username="testuser",
            hashed_password="hash",
            target_language="German"
        )
        db_session.add(user)
        db_session.commit()
        
        with patch('app.services.grammar.get_llm_client') as mock_get_llm, \
             patch('app.services.grammar.get_checker_service') as mock_get_checker, \
             patch('app.services.grammar.get_secondary_validator') as mock_get_validator:
            
            mock_llm = AsyncMock()
            mock_llm.generate = AsyncMock(return_value="Invalid JSON {not:valid}")
            mock_llm.close = AsyncMock()
            mock_get_llm.return_value = mock_llm
            
            mock_checker = AsyncMock()
            mock_checker.check_content = AsyncMock(return_value={"is_valid": True, "suggested_fix": None})
            mock_get_checker.return_value = mock_checker
            
            mock_validator = AsyncMock()
            mock_validator.deep_validate = AsyncMock(return_value={"is_approved": True, "improved_version": None, "confidence_score": 0.9})
            mock_get_validator.return_value = mock_validator
            
            with pytest.raises(ValueError, match="Failed to generate valid grammar question from AI"):
                await get_grammar_question(
                    user_id=user.id,
                    target_language="German",
                    level="A1",
                    topic=None,
                    db=db_session
                )
    
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
            "question_text": "Bad question",
            "options": ["a", "b"],
            "correct_option_index": 0,
            "explanation": "Bad"
        }
        
        fixed_json = {
            "question_text": "Good question",
            "options": ["a", "b", "c", "d"],
            "correct_option_index": 0,
            "explanation": "Good"
        }
        
        import json
        with patch('app.services.grammar.get_llm_client') as mock_get_llm, \
             patch('app.services.grammar.get_checker_service') as mock_get_checker, \
             patch('app.services.grammar.get_secondary_validator') as mock_get_validator:
            
            mock_llm = AsyncMock()
            mock_llm.generate = AsyncMock(return_value=f"```json\n{json.dumps(original_json)}\n```")
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
            
            result = await get_grammar_question(
                user_id=user.id,
                target_language="German",
                level="A1",
                topic=None,
                db=db_session
            )
            
            assert result.question_text == "Good question"
    
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
            "question_text": "Original question",
            "options": ["a", "b", "c", "d"],
            "correct_option_index": 0,
            "explanation": "Original"
        }
        
        improved_json = {
            "question_text": "Improved question",
            "options": ["a", "b", "c", "d"],
            "correct_option_index": 0,
            "explanation": "Improved"
        }
        
        import json
        with patch('app.services.grammar.get_llm_client') as mock_get_llm, \
             patch('app.services.grammar.get_checker_service') as mock_get_checker, \
             patch('app.services.grammar.get_secondary_validator') as mock_get_validator:
            
            mock_llm = AsyncMock()
            mock_llm.generate = AsyncMock(return_value=f"```json\n{json.dumps(original_json)}\n```")
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
            
            result = await get_grammar_question(
                user_id=user.id,
                target_language="German",
                level="A1",
                topic=None,
                db=db_session
            )
            
            assert result.question_text == "Improved question"
    
    @pytest.mark.asyncio
    async def test_json_with_backticks_stripped(self, db_session):
        """Test that backticks are properly stripped from JSON."""
        user = User(
            username="testuser",
            hashed_password="hash",
            target_language="German"
        )
        db_session.add(user)
        db_session.commit()
        
        question_json = {
            "question_text": "Test question",
            "options": ["a", "b", "c", "d"],
            "correct_option_index": 0,
            "explanation": "Test"
        }
        
        import json
        with patch('app.services.grammar.get_llm_client') as mock_get_llm, \
             patch('app.services.grammar.get_checker_service') as mock_get_checker, \
             patch('app.services.grammar.get_secondary_validator') as mock_get_validator:
            
            mock_llm = AsyncMock()
            # Test with ``` format (no json tag)
            mock_llm.generate = AsyncMock(return_value=f"```\n{json.dumps(question_json)}\n```")
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
                "is_approved": True,
                "improved_version": None,
                "confidence_score": 0.9
            })
            mock_get_validator.return_value = mock_validator
            
            result = await get_grammar_question(
                user_id=user.id,
                target_language="German",
                level="A1",
                topic=None,
                db=db_session
            )
            
            assert result.question_text == "Test question"
