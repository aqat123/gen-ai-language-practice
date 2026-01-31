"""
Integration tests for error handling in learning endpoints.
Tests that endpoints properly handle service-level errors and exceptions.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock


class TestVocabularyEndpointErrors:
    """Test vocabulary endpoint error handling."""
    
    def test_get_flashcard_handles_service_exception(self, authenticated_client: TestClient):
        """Test that get flashcard endpoint handles service exceptions gracefully."""
        authenticated_client.put("/api/v1/auth/me/language", json={"target_language": "German"})
        authenticated_client.put("/api/v1/auth/me/level", json={"level": "A1"})
        
        # Mock service to raise exception
        with patch('app.api.v1.endpoints.vocabulary.get_next_flashcard', new=AsyncMock(side_effect=Exception("LLM service unavailable"))):
            response = authenticated_client.get("/api/v1/vocabulary/next")
            
            assert response.status_code == 500
            assert "unavailable" in response.json()["detail"].lower()
    
    def test_submit_answer_with_invalid_word_raises_404(self, authenticated_client: TestClient):
        """Test that submitting answer for invalid word returns 404."""
        authenticated_client.put("/api/v1/auth/me/language", json={"target_language": "Spanish"})
        authenticated_client.put("/api/v1/auth/me/level", json={"level": "A2"})
        
        # Mock service to raise ValueError (not found)
        with patch('app.api.v1.endpoints.vocabulary.submit_vocabulary_answer', new=AsyncMock(side_effect=ValueError("Word not found"))):
            response = authenticated_client.post(
                "/api/v1/vocabulary/answer",
                json={"word": "nonexistent", "selected_option_index": 0, "correct_option_index": 1}
            )
            
            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()
    
    def test_submit_answer_handles_general_exception(self, authenticated_client: TestClient):
        """Test that submit answer handles unexpected exceptions."""
        authenticated_client.put("/api/v1/auth/me/language", json={"target_language": "French"})
        authenticated_client.put("/api/v1/auth/me/level", json={"level": "B1"})
        
        # Mock service to raise unexpected exception
        with patch('app.api.v1.endpoints.vocabulary.submit_vocabulary_answer', new=AsyncMock(side_effect=Exception("Database connection lost"))):
            response = authenticated_client.post(
                "/api/v1/vocabulary/answer",
                json={"word": "bonjour", "selected_option_index": 0, "correct_option_index": 0}
            )
            
            assert response.status_code == 500
            assert "database" in response.json()["detail"].lower()


class TestConversationEndpointErrors:
    """Test conversation endpoint error handling."""
    
    def test_start_conversation_handles_exception(self, authenticated_client: TestClient):
        """Test that start conversation handles service exceptions."""
        authenticated_client.put("/api/v1/auth/me/language", json={"target_language": "German"})
        authenticated_client.put("/api/v1/auth/me/level", json={"level": "B1"})
        
        # Mock service to raise exception
        with patch('app.api.v1.endpoints.conversation.start_conversation', new=AsyncMock(side_effect=Exception("AI service timeout"))):
            response = authenticated_client.post(
                "/api/v1/conversation/start",
                json={"topic": "food"}
            )
            
            assert response.status_code == 500
            assert "timeout" in response.json()["detail"].lower()
    
    def test_send_message_with_invalid_session_raises_404(self, authenticated_client: TestClient):
        """Test that sending message to invalid session returns 404."""
        authenticated_client.put("/api/v1/auth/me/language", json={"target_language": "Spanish"})
        authenticated_client.put("/api/v1/auth/me/level", json={"level": "A1"})
        
        # Mock service to raise ValueError (session not found)
        with patch('app.api.v1.endpoints.conversation.send_message', new=AsyncMock(side_effect=ValueError("Session not found"))):
            response = authenticated_client.post(
                "/api/v1/conversation/invalid-session-123/message",
                json={"message": "Hola"}
            )
            
            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()
    
    def test_send_message_handles_general_exception(self, authenticated_client: TestClient):
        """Test that send message handles unexpected exceptions."""
        authenticated_client.put("/api/v1/auth/me/language", json={"target_language": "French"})
        authenticated_client.put("/api/v1/auth/me/level", json={"level": "C1"})
        
        # Mock service to raise unexpected exception
        with patch('app.api.v1.endpoints.conversation.send_message', new=AsyncMock(side_effect=Exception("LLM API rate limit exceeded"))):
            response = authenticated_client.post(
                "/api/v1/conversation/some-session/message",
                json={"message": "Comment ça va?"}
            )
            
            assert response.status_code == 500
            assert "rate limit" in response.json()["detail"].lower()


class TestGrammarEndpointErrors:
    """Test grammar endpoint error handling."""
    
    def test_get_question_handles_exception(self, authenticated_client: TestClient):
        """Test that get grammar question handles service exceptions."""
        authenticated_client.put("/api/v1/auth/me/language", json={"target_language": "German"})
        authenticated_client.put("/api/v1/auth/me/level", json={"level": "A2"})
        
        # Mock service to raise exception
        with patch('app.api.v1.endpoints.grammar.get_grammar_question', new=AsyncMock(side_effect=Exception("Question generation failed"))):
            response = authenticated_client.get("/api/v1/grammar/question")
            
            assert response.status_code == 500
            assert "failed" in response.json()["detail"].lower()
    
    def test_submit_answer_with_invalid_question_raises_404(self, authenticated_client: TestClient):
        """Test that submitting answer for invalid question returns 404."""
        authenticated_client.put("/api/v1/auth/me/language", json={"target_language": "Spanish"})
        authenticated_client.put("/api/v1/auth/me/level", json={"level": "B2"})
        
        # Mock service to raise ValueError (question not found)
        with patch('app.api.v1.endpoints.grammar.submit_grammar_answer', new=AsyncMock(side_effect=ValueError("Question not found in database"))):
            response = authenticated_client.post(
                "/api/v1/grammar/answer",
                json={
                    "question_id": "invalid-123",
                    "selected_option_index": 0,
                    "correct_option_index": 1
                }
            )
            
            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()
    
    def test_submit_answer_handles_general_exception(self, authenticated_client: TestClient):
        """Test that submit grammar answer handles unexpected exceptions."""
        authenticated_client.put("/api/v1/auth/me/language", json={"target_language": "French"})
        authenticated_client.put("/api/v1/auth/me/level", json={"level": "C2"})
        
        # Mock service to raise unexpected exception
        with patch('app.api.v1.endpoints.grammar.submit_grammar_answer', new=AsyncMock(side_effect=Exception("Progress update failed"))):
            response = authenticated_client.post(
                "/api/v1/grammar/answer",
                json={
                    "question_id": "test-q-456",
                    "selected_option_index": 2,
                    "correct_option_index": 2
                }
            )
            
            assert response.status_code == 500
            assert "progress" in response.json()["detail"].lower() or "failed" in response.json()["detail"].lower()
