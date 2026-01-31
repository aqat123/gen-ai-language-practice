"""
Unit tests for conversation service.

Tests:
- Conversation session creation
- Message handling
- Context management
- Progress tracking
"""

import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from app.services.conversation import (
    start_conversation,
    send_message
)
from app.db.models import User, ConversationSession
from app.schemas.conversation import (
    ConversationStartRequest,
    ConversationMessageRequest
)


class TestConversationStarting:
    """Test conversation session creation."""
    
    @pytest.mark.asyncio
    async def test_start_conversation_creates_session(self, db_session):
        """Test that starting a conversation creates a session."""
        user = User(
            username="testuser",
            hashed_password="hash",
            target_language="French",
            level="A1"
        )
        db_session.add(user)
        db_session.commit()
        
        initial_session_count = db_session.query(ConversationSession).count()
        
        with patch('app.services.conversation.get_llm_client') as mock_get_llm, \
             patch('app.services.conversation.get_checker_service') as mock_get_checker:
            
            mock_llm = AsyncMock()
            mock_llm.generate = AsyncMock(return_value="Bonjour! Comment ça va?")
            mock_llm.close = AsyncMock()
            mock_get_llm.return_value = mock_llm
            
            mock_checker = AsyncMock()
            mock_checker.check_content = AsyncMock(return_value={"is_valid": True, "suggested_fix": None})
            mock_get_checker.return_value = mock_checker
            
            result = await start_conversation(
                user=user,
                request=ConversationStartRequest(topic="greetings"),
                db=db_session
            )
        
        assert result is not None
        assert result.opening_message is not None
        final_session_count = db_session.query(ConversationSession).count()
        assert final_session_count > initial_session_count
    
    @pytest.mark.asyncio
    async def test_start_conversation_returns_session_id(self, db_session):
        """Test that starting conversation returns session ID."""
        user = User(
            username="testuser",
            hashed_password="hash",
            target_language="German",
            level="B1"
        )
        db_session.add(user)
        db_session.commit()
        
        with patch('app.services.conversation.get_llm_client') as mock_get_llm, \
             patch('app.services.conversation.get_checker_service') as mock_get_checker:
            
            mock_llm = AsyncMock()
            mock_llm.generate = AsyncMock(return_value="Hallo! Wie geht's?")
            mock_llm.close = AsyncMock()
            mock_get_llm.return_value = mock_llm
            
            mock_checker = AsyncMock()
            mock_checker.check_content = AsyncMock(return_value={"is_valid": True, "suggested_fix": None})
            mock_get_checker.return_value = mock_checker
            
            result = await start_conversation(
                user=user,
                request=ConversationStartRequest(),
                db=db_session
            )
        
        assert result.session_id is not None
        assert len(result.session_id) > 0
    
    @pytest.mark.asyncio
    async def test_start_conversation_without_topic(self, db_session):
        """Test starting conversation without specific topic."""
        user = User(
            username="testuser",
            hashed_password="hash",
            target_language="Spanish",
            level="A2"
        )
        db_session.add(user)
        db_session.commit()
        
        with patch('app.services.conversation.get_llm_client') as mock_get_llm, \
             patch('app.services.conversation.get_checker_service') as mock_get_checker:
            
            mock_llm = AsyncMock()
            mock_llm.generate = AsyncMock(return_value="¡Hola! ¿Cómo estás?")
            mock_llm.close = AsyncMock()
            mock_get_llm.return_value = mock_llm
            
            mock_checker = AsyncMock()
            mock_checker.check_content = AsyncMock(return_value={"is_valid": True, "suggested_fix": None})
            mock_get_checker.return_value = mock_checker
            
            result = await start_conversation(
                user=user,
                request=ConversationStartRequest(),
                db=db_session
            )
        
        assert result is not None
        assert result.opening_message is not None

    @pytest.mark.asyncio
    async def test_start_conversation_uses_suggested_fix_when_invalid(self, db_session):
        """Test that conversation uses suggested_fix when checker finds issues."""
        user = User(
            username="testuser",
            hashed_password="hash",
            target_language="French",
            level="A1"
        )
        db_session.add(user)
        db_session.commit()
        
        with patch('app.services.conversation.get_llm_client') as mock_get_llm, \
             patch('app.services.conversation.get_checker_service') as mock_get_checker:
            
            mock_llm = AsyncMock()
            mock_llm.generate = AsyncMock(return_value="This is invalid content")
            mock_llm.close = AsyncMock()
            mock_get_llm.return_value = mock_llm
            
            mock_checker = AsyncMock()
            # Checker returns invalid with a suggested fix
            mock_checker.check_content = AsyncMock(return_value={
                "is_valid": False, 
                "suggested_fix": "Bonjour! Comment allez-vous?"
            })
            mock_get_checker.return_value = mock_checker
            
            result = await start_conversation(
                user=user,
                request=ConversationStartRequest(topic="greetings"),
                db=db_session
            )
        
        # Should use the suggested_fix instead of the original message
        assert result.opening_message == "Bonjour! Comment allez-vous?"


class TestConversationMessageHandling:
    """Test conversation message sending and receiving."""
    
    @pytest.mark.asyncio
    async def test_send_message_returns_response(self, db_session):
        """Test that sending a message returns AI response."""
        user = User(
            username="testuser",
            hashed_password="hash",
            target_language="Italian",
            level="A1"
        )
        db_session.add(user)
        db_session.commit()
        
        # First start a conversation
        with patch('app.services.conversation.get_llm_client') as mock_get_llm, \
             patch('app.services.conversation.get_checker_service') as mock_get_checker:
            
            mock_llm = AsyncMock()
            mock_llm.generate = AsyncMock(return_value="Ciao!")
            mock_llm.close = AsyncMock()
            mock_get_llm.return_value = mock_llm
            
            mock_checker = AsyncMock()
            mock_checker.check_content = AsyncMock(return_value={"is_valid": True, "suggested_fix": None})
            mock_get_checker.return_value = mock_checker
            
            start_result = await start_conversation(
                user=user,
                request=ConversationStartRequest(),
                db=db_session
            )
            session_id = start_result.session_id
        
        # Now send a message
        with patch('app.services.conversation.get_llm_client') as mock_get_llm, \
             patch('app.services.conversation.get_checker_service') as mock_get_checker:
            
            mock_llm = AsyncMock()
            mock_llm.generate = AsyncMock(side_effect=["Come stai?", '{"corrected_message": null, "tips": null}'])
            mock_llm.close = AsyncMock()
            mock_get_llm.return_value = mock_llm
            
            mock_checker = AsyncMock()
            mock_checker.check_content = AsyncMock(return_value={"is_valid": True, "suggested_fix": None})
            mock_get_checker.return_value = mock_checker
            
            result = await send_message(
                session_id=session_id,
                user=user,
                request=ConversationMessageRequest(message="Hello!"),
                db=db_session
            )
        
        assert result is not None
        assert result.reply is not None
    
    @pytest.mark.asyncio
    async def test_send_message_with_corrections(self, db_session):
        """Test that conversation provides corrections when needed."""
        user = User(
            username="testuser",
            hashed_password="hash",
            target_language="Russian",
            level="A2"
        )
        db_session.add(user)
        db_session.commit()
        
        # Start conversation
        with patch('app.services.conversation.get_llm_client') as mock_get_llm, \
             patch('app.services.conversation.get_checker_service') as mock_get_checker:
            
            mock_llm = AsyncMock()
            mock_llm.generate = AsyncMock(return_value="Привет!")
            mock_llm.close = AsyncMock()
            mock_get_llm.return_value = mock_llm
            
            mock_checker = AsyncMock()
            mock_checker.check_content = AsyncMock(return_value={"is_valid": True, "suggested_fix": None})
            mock_get_checker.return_value = mock_checker
            
            start_result = await start_conversation(
                user=user,
                request=ConversationStartRequest(),
                db=db_session
            )
            session_id = start_result.session_id
        
        # Send message with correction
        with patch('app.services.conversation.get_llm_client') as mock_get_llm, \
             patch('app.services.conversation.get_checker_service') as mock_get_checker:
            
            mock_llm = AsyncMock()
            correction_json = '{"corrected_message": "Я хорошо", "tips": "Use \'я\' for I"}'
            mock_llm.generate = AsyncMock(side_effect=["Отлично!", correction_json])
            mock_llm.close = AsyncMock()
            mock_get_llm.return_value = mock_llm
            
            mock_checker = AsyncMock()
            mock_checker.check_content = AsyncMock(return_value={"is_valid": True, "suggested_fix": None})
            mock_get_checker.return_value = mock_checker
            
            result = await send_message(
                session_id=session_id,
                user=user,
                request=ConversationMessageRequest(message="I good"),
                db=db_session
            )
        
        assert result.reply is not None
        assert result.corrected_user_message is not None
        assert result.tips is not None


class TestConversationEdgeCases:
    """Test edge cases in conversation service."""
    
    @pytest.mark.asyncio
    async def test_send_message_with_invalid_session_id(self, db_session):
        """Test sending message with non-existent session."""
        user = User(
            username="testuser",
            hashed_password="hash",
            target_language="Korean",
            level="B1"
        )
        db_session.add(user)
        db_session.commit()
        
        with pytest.raises(ValueError):
            await send_message(
                session_id="invalid_session_id",
                user=user,
                request=ConversationMessageRequest(message="Hello"),
                db=db_session
            )
    
    @pytest.mark.asyncio
    async def test_send_message_wrong_user(self, db_session):
        """Test sending message to another user's session."""
        user1 = User(
            username="testuser1",
            hashed_password="hash",
            target_language="Chinese",
            level="A1"
        )
        user2 = User(
            username="testuser2",
            hashed_password="hash",
            target_language="Chinese",
            level="A1"
        )
        db_session.add_all([user1, user2])
        db_session.commit()
        
        # Start conversation as user1
        with patch('app.services.conversation.get_llm_client') as mock_get_llm, \
             patch('app.services.conversation.get_checker_service') as mock_get_checker:
            
            mock_llm = AsyncMock()
            mock_llm.generate = AsyncMock(return_value="你好!")
            mock_llm.close = AsyncMock()
            mock_get_llm.return_value = mock_llm
            
            mock_checker = AsyncMock()
            mock_checker.check_content = AsyncMock(return_value={"is_valid": True, "suggested_fix": None})
            mock_get_checker.return_value = mock_checker
            
            start_result = await start_conversation(
                user=user1,
                request=ConversationStartRequest(),
                db=db_session
            )
            session_id = start_result.session_id
        
        # user2 tries to use user1's session
        with pytest.raises(ValueError):
            await send_message(
                session_id=session_id,
                user=user2,
                request=ConversationMessageRequest(message="Hello"),
                db=db_session
            )
    
    @pytest.mark.asyncio
    async def test_checker_suggests_fix(self, db_session):
        """Test that checker's suggested fix is used when content is invalid."""
        user = User(
            username="testuser",
            hashed_password="hash",
            target_language="Arabic",
            level="B1"
        )
        db_session.add(user)
        db_session.commit()
        
        # Start conversation
        with patch('app.services.conversation.get_llm_client') as mock_get_llm, \
             patch('app.services.conversation.get_checker_service') as mock_get_checker:
            
            mock_llm = AsyncMock()
            mock_llm.generate = AsyncMock(return_value="مرحبا!")
            mock_llm.close = AsyncMock()
            mock_get_llm.return_value = mock_llm
            
            mock_checker = AsyncMock()
            mock_checker.check_content = AsyncMock(return_value={"is_valid": True, "suggested_fix": None})
            mock_get_checker.return_value = mock_checker
            
            start_result = await start_conversation(
                user=user,
                request=ConversationStartRequest(),
                db=db_session
            )
            session_id = start_result.session_id
        
        # Send message where checker suggests fix
        with patch('app.services.conversation.get_llm_client') as mock_get_llm, \
             patch('app.services.conversation.get_checker_service') as mock_get_checker:
            
            mock_llm = AsyncMock()
            mock_llm.generate = AsyncMock(side_effect=["Bad content", '{"corrected_message": null, "tips": null}'])
            mock_llm.close = AsyncMock()
            mock_get_llm.return_value = mock_llm
            
            mock_checker = AsyncMock()
            mock_checker.check_content = AsyncMock(return_value={
                "is_valid": False,
                "suggested_fix": "Fixed content"
            })
            mock_get_checker.return_value = mock_checker
            
            result = await send_message(
                session_id=session_id,
                user=user,
                request=ConversationMessageRequest(message="Hello"),
                db=db_session
            )
        
        assert result.reply == "Fixed content"


class TestConversationProgressTracking:
    """Test progress tracking in conversations."""
    
    @pytest.mark.asyncio
    async def test_send_message_creates_progress_record(self, db_session):
        """Test that sending messages creates progress record."""
        user = User(
            username="testuser",
            hashed_password="hash",
            target_language="Turkish",
            level="A1"
        )
        db_session.add(user)
        db_session.commit()
        
        # Start conversation
        with patch('app.services.conversation.get_llm_client') as mock_get_llm, \
             patch('app.services.conversation.get_checker_service') as mock_get_checker:
            
            mock_llm = AsyncMock()
            mock_llm.generate = AsyncMock(return_value="Merhaba!")
            mock_llm.close = AsyncMock()
            mock_get_llm.return_value = mock_llm
            
            mock_checker = AsyncMock()
            mock_checker.check_content = AsyncMock(return_value={"is_valid": True, "suggested_fix": None})
            mock_get_checker.return_value = mock_checker
            
            start_result = await start_conversation(
                user=user,
                request=ConversationStartRequest(),
                db=db_session
            )
            session_id = start_result.session_id
        
        # Send message
        with patch('app.services.conversation.get_llm_client') as mock_get_llm, \
             patch('app.services.conversation.get_checker_service') as mock_get_checker:
            
            mock_llm = AsyncMock()
            mock_llm.generate = AsyncMock(side_effect=["Nasılsın?", '{"corrected_message": null, "tips": null}'])
            mock_llm.close = AsyncMock()
            mock_get_llm.return_value = mock_llm
            
            mock_checker = AsyncMock()
            mock_checker.check_content = AsyncMock(return_value={"is_valid": True, "suggested_fix": None})
            mock_get_checker.return_value = mock_checker
            
            await send_message(
                session_id=session_id,
                user=user,
                request=ConversationMessageRequest(message="Hello"),
                db=db_session
            )
        
        # Check progress record exists
        from app.db.models import UserProgress
        progress = db_session.query(UserProgress).filter(
            UserProgress.user_id == user.id,
            UserProgress.module == "conversation"
        ).first()
        
        assert progress is not None
        assert progress.total_attempts >= 1


class TestConversationJSONParsing:
    """Test JSON parsing edge cases in conversation service."""
    
    @pytest.mark.asyncio
    async def test_correction_json_with_backticks_stripped(self, db_session):
        """Test that backticks are properly stripped from correction JSON."""
        user = User(
            username="testuser",
            hashed_password="hash",
            target_language="German"
        )
        db_session.add(user)
        db_session.commit()
        
        # Create session first
        session = ConversationSession(
            id=str(uuid4()),
            user_id=user.id,
            target_language="German",
            context_json={"messages": []}
        )
        db_session.add(session)
        db_session.commit()
        session_id = session.id
        
        with patch('app.services.conversation.get_llm_client') as mock_get_llm, \
             patch('app.services.conversation.get_checker_service') as mock_get_checker:
            
            mock_llm = AsyncMock()
            mock_llm.generate = AsyncMock(side_effect=[
                "Hallo!",
                '```json\n{"corrected_message": "Ich bin gut", "tips": "Great job!"}\n```'
            ])
            mock_llm.close = AsyncMock()
            mock_get_llm.return_value = mock_llm
            
            mock_checker = AsyncMock()
            mock_checker.check_content = AsyncMock(return_value={"is_valid": True, "suggested_fix": None})
            mock_get_checker.return_value = mock_checker
            
            result = await send_message(
                session_id=session_id,
                user=user,
                request=ConversationMessageRequest(message="Ich gut"),
                db=db_session
            )
            
            assert result.corrected_user_message == "Ich bin gut"
            assert result.tips == "Great job!"
    
    @pytest.mark.asyncio
    async def test_correction_invalid_json_handled(self, db_session):
        """Test that invalid correction JSON doesn't crash."""
        user = User(
            username="testuser",
            hashed_password="hash",
            target_language="Spanish"
        )
        db_session.add(user)
        db_session.commit()
        
        # Create session first
        session = ConversationSession(
            id=str(uuid4()),
            user_id=user.id,
            target_language="Spanish",
            context_json={"messages": []}
        )
        db_session.add(session)
        db_session.commit()
        session_id = session.id
        
        with patch('app.services.conversation.get_llm_client') as mock_get_llm, \
             patch('app.services.conversation.get_checker_service') as mock_get_checker:
            
            mock_llm = AsyncMock()
            mock_llm.generate = AsyncMock(side_effect=[
                "¡Hola!",
                "This is not valid JSON at all"
            ])
            mock_llm.close = AsyncMock()
            mock_get_llm.return_value = mock_llm
            
            mock_checker = AsyncMock()
            mock_checker.check_content = AsyncMock(return_value={"is_valid": True, "suggested_fix": None})
            mock_get_checker.return_value = mock_checker
            
            result = await send_message(
                session_id=session_id,
                user=user,
                request=ConversationMessageRequest(message="Hola"),
                db=db_session
            )
            
            # Should not crash, correction should be None
            assert result.corrected_user_message is None
            assert result.tips is None
    
    @pytest.mark.asyncio
    async def test_correction_null_string_handled(self, db_session):
        """Test that string 'null' in correction JSON is handled correctly."""
        user = User(
            username="testuser",
            hashed_password="hash",
            target_language="French"
        )
        db_session.add(user)
        db_session.commit()
        
        # Create session first
        session = ConversationSession(
            id=str(uuid4()),
            user_id=user.id,
            target_language="French",
            context_json={"messages": []}
        )
        db_session.add(session)
        db_session.commit()
        session_id = session.id
        
        with patch('app.services.conversation.get_llm_client') as mock_get_llm, \
             patch('app.services.conversation.get_checker_service') as mock_get_checker:
            
            mock_llm = AsyncMock()
            mock_llm.generate = AsyncMock(side_effect=[
                "Bonjour!",
                '{"corrected_message": "null", "tips": "null"}'
            ])
            mock_llm.close = AsyncMock()
            mock_get_llm.return_value = mock_llm
            
            mock_checker = AsyncMock()
            mock_checker.check_content = AsyncMock(return_value={"is_valid": True, "suggested_fix": None})
            mock_get_checker.return_value = mock_checker
            
            result = await send_message(
                session_id=session_id,
                user=user,
                request=ConversationMessageRequest(message="Bonjour"),
                db=db_session
            )
            
            # String "null" should be treated as None
            assert result.corrected_user_message is None
            assert result.tips is None

    @pytest.mark.asyncio
    async def test_send_message_creates_user_progress_if_not_exists(self, db_session):
        """Test that sending a message creates UserProgress if it doesn't exist."""
        user = User(
            username="newconvouser",
            hashed_password="hash",
            target_language="Spanish",
            level="A1"
        )
        db_session.add(user)
        db_session.commit()
        
        # Start conversation
        with patch('app.services.conversation.get_llm_client') as mock_get_llm, \
             patch('app.services.conversation.get_checker_service') as mock_get_checker:
            
            mock_llm = AsyncMock()
            mock_llm.generate = AsyncMock(return_value="¡Hola! ¿Cómo estás?")
            mock_llm.close = AsyncMock()
            mock_get_llm.return_value = mock_llm
            
            mock_checker = AsyncMock()
            mock_checker.check_content = AsyncMock(return_value={"is_valid": True, "suggested_fix": None})
            mock_get_checker.return_value = mock_checker
            
            start_result = await start_conversation(
                user=user,
                request=ConversationStartRequest(topic="food"),
                db=db_session
            )
            session_id = start_result.session_id
        
        # Verify no UserProgress exists yet
        from app.db.models import UserProgress
        progress = db_session.query(UserProgress).filter(
            UserProgress.user_id == user.id,
            UserProgress.module == "conversation"
        ).first()
        assert progress is None
        
        # Send message - this should create UserProgress
        with patch('app.services.conversation.get_llm_client') as mock_get_llm, \
             patch('app.services.conversation.get_checker_service') as mock_get_checker:
            
            mock_llm = AsyncMock()
            mock_llm.generate = AsyncMock(side_effect=["Muy bien!", '{"corrected_message": null, "tips": null}'])
            mock_llm.close = AsyncMock()
            mock_get_llm.return_value = mock_llm
            
            mock_checker = AsyncMock()
            mock_checker.check_content = AsyncMock(return_value={"is_valid": True, "suggested_fix": None})
            mock_get_checker.return_value = mock_checker
            
            result = await send_message(
                session_id=session_id,
                user=user,
                request=ConversationMessageRequest(message="Estoy bien"),
                db=db_session
            )
        
        # Verify UserProgress was created
        progress = db_session.query(UserProgress).filter(
            UserProgress.user_id == user.id,
            UserProgress.module == "conversation"
        ).first()
        assert progress is not None
        assert progress.total_attempts == 1
        assert result.reply is not None
