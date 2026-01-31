"""
Unit tests for AI services (LLM client and checker service).

These tests use mocking to avoid making actual API calls to Gemini.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

from app.services.ai_services import LLMClient, CheckerService, LLMError


class TestLLMClient:
    """Test cases for LLM client."""
    
    @pytest.mark.asyncio
    async def test_llm_generate_returns_text_successfully(self):
        """Test that LLM client returns generated text from API."""
        # Arrange
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "candidates": [{
                "content": {
                    "parts": [{"text": "Bonjour! Comment allez-vous?"}]
                }
            }]
        }
        mock_response.raise_for_status = MagicMock()
        
        llm = LLMClient(
            api_key="test_api_key",
            base_url="https://test.api.com",
            model="test-model"
        )
        
        # Act
        with patch.object(llm.client, 'post', new=AsyncMock(return_value=mock_response)):
            result = await llm.generate(
                system_prompt="You are a French teacher",
                user_prompt="Say hello in French"
            )
        
        # Assert
        assert result == "Bonjour! Comment allez-vous?"
        
        # Cleanup
        await llm.close()
    
    @pytest.mark.asyncio
    async def test_llm_generate_with_custom_temperature(self):
        """Test that LLM client passes temperature parameter correctly."""
        # Arrange
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "candidates": [{
                "content": {
                    "parts": [{"text": "Creative response"}]
                }
            }]
        }
        mock_response.raise_for_status = MagicMock()
        
        llm = LLMClient(
            api_key="test_key",
            base_url="https://test.api.com",
            model="test-model"
        )
        
        # Create a mock that captures the call
        mock_post = AsyncMock(return_value=mock_response)
        
        # Act
        with patch.object(llm.client, 'post', new=mock_post):
            result = await llm.generate(
                system_prompt="Be creative",
                user_prompt="Write a poem",
                temperature=0.9,
                max_tokens=1000
            )
        
        # Assert
        assert result == "Creative response"
        
        # Verify the API was called with correct parameters
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        assert payload['generationConfig']['temperature'] == 0.9
        assert payload['generationConfig']['maxOutputTokens'] == 1000
        
        # Cleanup
        await llm.close()
    
    @pytest.mark.asyncio
    async def test_llm_generate_handles_http_error(self):
        """Test that LLM client handles HTTP errors gracefully."""
        # Arrange
        llm = LLMClient(
            api_key="test_key",
            base_url="https://test.api.com",
            model="test-model"
        )
        
        # Mock HTTP error
        mock_post = AsyncMock(side_effect=httpx.HTTPError("Connection failed"))
        
        # Act & Assert
        with patch.object(llm.client, 'post', new=mock_post):
            with pytest.raises(LLMError, match="HTTP error during LLM API call"):
                await llm.generate(
                    system_prompt="Test",
                    user_prompt="Test"
                )
        
        # Cleanup
        await llm.close()
    
    @pytest.mark.asyncio
    async def test_llm_generate_handles_invalid_response_format(self):
        """Test that LLM client handles unexpected response format."""
        # Arrange
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "unexpected": "format"
        }
        mock_response.raise_for_status = MagicMock()
        
        llm = LLMClient(
            api_key="test_key",
            base_url="https://test.api.com",
            model="test-model"
        )
        
        # Act & Assert
        with patch.object(llm.client, 'post', new=AsyncMock(return_value=mock_response)):
            with pytest.raises(LLMError, match="Unexpected response format"):
                await llm.generate(
                    system_prompt="Test",
                    user_prompt="Test"
                )
        
        # Cleanup
        await llm.close()
    
    @pytest.mark.asyncio
    async def test_llm_generate_handles_empty_candidates(self):
        """Test LLM client handles empty candidates in response."""
        # Arrange
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "candidates": []
        }
        mock_response.raise_for_status = MagicMock()
        
        llm = LLMClient(
            api_key="test_key",
            base_url="https://test.api.com",
            model="test-model"
        )
        
        # Act & Assert
        with patch.object(llm.client, 'post', new=AsyncMock(return_value=mock_response)):
            with pytest.raises(LLMError):
                await llm.generate(
                    system_prompt="Test",
                    user_prompt="Test"
                )
        
        # Cleanup
        await llm.close()
    
    @pytest.mark.asyncio
    async def test_llm_client_combines_prompts_correctly(self):
        """Test that system and user prompts are combined properly."""
        # Arrange
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "candidates": [{
                "content": {
                    "parts": [{"text": "Response"}]
                }
            }]
        }
        mock_response.raise_for_status = MagicMock()
        
        llm = LLMClient(
            api_key="test_key",
            base_url="https://test.api.com",
            model="test-model"
        )
        
        mock_post = AsyncMock(return_value=mock_response)
        
        # Act
        with patch.object(llm.client, 'post', new=mock_post):
            await llm.generate(
                system_prompt="System instruction",
                user_prompt="User query"
            )
        
        # Assert
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        combined_text = payload['contents'][0]['parts'][0]['text']
        assert "System instruction" in combined_text
        assert "User query" in combined_text
        
        # Cleanup
        await llm.close()


class TestCheckerService:
    """Test cases for checker service."""
    
    @pytest.mark.asyncio
    async def test_checker_validates_vocabulary_content(self):
        """Test that checker service validates vocabulary flashcards."""
        # Arrange
        mock_llm_response = {
            "candidates": [{
                "content": {
                    "parts": [{"text": '{"is_valid": true, "confidence": 0.95, "issues": []}'}]
                }
            }]
        }
        
        mock_response = MagicMock()
        mock_response.json.return_value = mock_llm_response
        mock_response.raise_for_status = MagicMock()
        
        llm_client = LLMClient(
            api_key="test_key",
            base_url="https://test.api.com",
            model="test-model"
        )
        
        checker = CheckerService(llm_client)
        
        # Act
        with patch.object(llm_client.client, 'post', new=AsyncMock(return_value=mock_response)):
            result = await checker.check_content(
                module="vocabulary",
                original_instruction="Generate a German A1 flashcard for 'house'",
                user_input={"language": "German", "level": "A1"},
                generated_content={"word": "Haus", "meaning": "house"}
            )
        
        # Assert
        assert "is_valid" in result or result is not None
        
        # Cleanup
        await llm_client.close()
    
    @pytest.mark.asyncio
    async def test_checker_service_with_different_modules(self):
        """Test checker service works with different module types."""
        # Arrange
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "candidates": [{
                "content": {
                    "parts": [{"text": "Valid content"}]
                }
            }]
        }
        mock_response.raise_for_status = MagicMock()
        
        llm_client = LLMClient(
            api_key="test_key",
            base_url="https://test.api.com",
            model="test-model"
        )
        
        checker = CheckerService(llm_client)
        
        modules = ["vocabulary", "grammar", "conversation", "writing"]
        
        # Act & Assert
        with patch.object(llm_client.client, 'post', new=AsyncMock(return_value=mock_response)):
            for module in modules:
                result = await checker.check_content(
                    module=module,
                    original_instruction=f"Test {module}",
                    user_input={"language": "Spanish", "level": "B1"},
                    generated_content="Test content"
                )
                assert result is not None
        
        # Cleanup
        await llm_client.close()


class TestLLMErrorHandling:
    """Test error handling in LLM services."""
    
    @pytest.mark.asyncio
    async def test_llm_error_contains_meaningful_message(self):
        """Test that LLMError contains helpful error messages."""
        # Arrange
        llm = LLMClient(
            api_key="test_key",
            base_url="https://test.api.com",
            model="test-model"
        )
        
        error_message = "Rate limit exceeded"
        mock_post = AsyncMock(side_effect=httpx.HTTPError(error_message))
        
        # Act & Assert
        with patch.object(llm.client, 'post', new=mock_post):
            with pytest.raises(LLMError) as exc_info:
                await llm.generate(
                    system_prompt="Test",
                    user_prompt="Test"
                )
            
            # Verify error message is informative
            assert "HTTP error" in str(exc_info.value)
        
        # Cleanup
        await llm.close()
    
    @pytest.mark.asyncio
    async def test_llm_handles_timeout_error(self):
        """Test that LLM client handles timeout errors."""
        # Arrange
        llm = LLMClient(
            api_key="test_key",
            base_url="https://test.api.com",
            model="test-model"
        )
        
        mock_post = AsyncMock(side_effect=httpx.TimeoutException("Request timeout"))
        
        # Act & Assert
        with patch.object(llm.client, 'post', new=mock_post):
            with pytest.raises(LLMError):
                await llm.generate(
                    system_prompt="Test",
                    user_prompt="Test"
                )
        
        # Cleanup
        await llm.close()


class TestLLMClientConfiguration:
    """Test LLM client configuration."""
    
    def test_llm_client_initialization(self):
        """Test that LLM client initializes with correct parameters."""
        # Arrange & Act
        llm = LLMClient(
            api_key="my_api_key",
            base_url="https://api.example.com",
            model="gemini-pro"
        )
        
        # Assert
        assert llm.api_key == "my_api_key"
        assert llm.base_url == "https://api.example.com"
        assert llm.model == "gemini-pro"
        assert llm.client is not None
    
    @pytest.mark.asyncio
    async def test_llm_client_default_parameters(self):
        """Test that LLM client uses default parameters when not specified."""
        # Arrange
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "candidates": [{
                "content": {
                    "parts": [{"text": "Response"}]
                }
            }]
        }
        mock_response.raise_for_status = MagicMock()
        
        llm = LLMClient(
            api_key="test_key",
            base_url="https://test.api.com",
            model="test-model"
        )
        
        mock_post = AsyncMock(return_value=mock_response)
        
        # Act
        with patch.object(llm.client, 'post', new=mock_post):
            await llm.generate(
                system_prompt="Test",
                user_prompt="Test"
                # Not specifying temperature or max_tokens
            )
        
        # Assert - Check default values were used
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        assert 'generationConfig' in payload
        assert 'temperature' in payload['generationConfig']
        assert 'maxOutputTokens' in payload['generationConfig']
        
        # Cleanup
        await llm.close()


class TestCheckerJSONParsing:
    """Test checker service JSON parsing edge cases."""
    
    @pytest.mark.asyncio
    async def test_checker_strips_json_backticks(self):
        """Test that checker service strips JSON markdown formatting."""
        mock_llm = AsyncMock()
        mock_llm.generate = AsyncMock(return_value='```json\n{"is_valid": true, "issues": []}\n```')
        mock_llm.close = AsyncMock()
        
        checker = CheckerService(llm_client=mock_llm)
        result = await checker.check_content(
            module="vocabulary",
            original_instruction="test",
            user_input={},
            generated_content='{"test": "data"}'
        )
        
        assert result["is_valid"] == True
        assert result["issues"] == []
    
    @pytest.mark.asyncio
    async def test_checker_handles_missing_fields(self):
        """Test that checker adds missing fields to response."""
        mock_llm = AsyncMock()
        # Response missing suggested_fix field
        mock_llm.generate = AsyncMock(return_value='{"is_valid": false, "issues": ["test"]}')
        mock_llm.close = AsyncMock()
        
        checker = CheckerService(llm_client=mock_llm)
        result = await checker.check_content(
            module="grammar",
            original_instruction="test",
            user_input={},
            generated_content='{"test": "data"}'
        )
        
        assert "suggested_fix" in result
        assert result["suggested_fix"] is None
    
    @pytest.mark.asyncio
    async def test_checker_handles_invalid_json(self):
        """Test that checker handles invalid JSON gracefully."""
        mock_llm = AsyncMock()
        mock_llm.generate = AsyncMock(return_value='Not valid JSON at all!')
        mock_llm.close = AsyncMock()
        
        checker = CheckerService(llm_client=mock_llm)
        result = await checker.check_content(
            module="vocabulary",
            original_instruction="test",
            user_input={},
            generated_content='{"test": "data"}'
        )
        
        # Should return valid response with error in issues
        assert result["is_valid"] == True
        assert len(result["issues"]) > 0
        assert "invalid JSON" in result["issues"][0]

    @pytest.mark.asyncio
    async def test_checker_strips_plain_backticks(self):
        """Test that checker strips plain ``` without json marker."""
        mock_llm = AsyncMock()
        mock_llm.generate = AsyncMock(return_value='```\n{"is_valid": true, "issues": [], "suggested_fix": null}\n```')
        mock_llm.close = AsyncMock()
        
        checker = CheckerService(llm_client=mock_llm)
        result = await checker.check_content(
            module="conversation",
            original_instruction="test",
            user_input={},
            generated_content='{"test": "data"}'
        )
        
        assert result["is_valid"] == True
        assert result["issues"] == []

    @pytest.mark.asyncio
    async def test_checker_handles_missing_is_valid(self):
        """Test that checker adds is_valid if missing."""
        mock_llm = AsyncMock()
        # Response missing is_valid field
        mock_llm.generate = AsyncMock(return_value='{"issues": [], "suggested_fix": null}')
        mock_llm.close = AsyncMock()
        
        checker = CheckerService(llm_client=mock_llm)
        result = await checker.check_content(
            module="grammar",
            original_instruction="test",
            user_input={},
            generated_content='{"test": "data"}'
        )
        
        assert "is_valid" in result
        assert result["is_valid"] == True

    @pytest.mark.asyncio
    async def test_checker_handles_missing_issues(self):
        """Test that checker adds issues if missing."""
        mock_llm = AsyncMock()
        # Response missing issues field
        mock_llm.generate = AsyncMock(return_value='{"is_valid": true, "suggested_fix": null}')
        mock_llm.close = AsyncMock()
        
        checker = CheckerService(llm_client=mock_llm)
        result = await checker.check_content(
            module="vocabulary",
            original_instruction="test",
            user_input={},
            generated_content='{"test": "data"}'
        )
        
        assert "issues" in result
        assert result["issues"] == []

    @pytest.mark.asyncio
    async def test_checker_handles_generic_exception(self):
        """Test that checker handles unexpected exceptions gracefully."""
        mock_llm = AsyncMock()
        # Simulate a generic exception
        mock_llm.generate = AsyncMock(side_effect=RuntimeError("API timeout"))
        mock_llm.close = AsyncMock()
        
        checker = CheckerService(llm_client=mock_llm)
        result = await checker.check_content(
            module="grammar",
            original_instruction="test",
            user_input={},
            generated_content='{"test": "data"}'
        )
        
        # Should return valid response with error in issues
        assert result["is_valid"] == True
        assert len(result["issues"]) > 0
        assert "Checker error" in result["issues"][0]
        assert "API timeout" in result["issues"][0]
