from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum


class ConversationState(Enum):
    INITIAL = "initial"
    WAITING_FOR_ORIGIN = "waiting_for_origin"
    WAITING_FOR_DESTINATION = "waiting_for_destination"
    WAITING_FOR_BOTH = "waiting_for_both"
    COMPLETED = "completed"
    MAX_RETRIES_REACHED = "max_retries_reached"


@dataclass
class ConversationContext:
    conversation_id: str
    user_id: Optional[str] = None
    state: ConversationState = ConversationState.INITIAL
    original_input: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    collected_data: Dict[str, Any] = field(default_factory=dict)
    validation_history: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    
    def update_state(self, new_state: ConversationState):
        self.state = new_state
        self.updated_at = datetime.now()
        
        if new_state == ConversationState.COMPLETED:
            self.expires_at = datetime.now() + timedelta(hours=24)
        elif new_state == ConversationState.MAX_RETRIES_REACHED:
            self.expires_at = datetime.now() + timedelta(hours=1)
    
    def increment_retry(self):
        self.retry_count += 1
        self.updated_at = datetime.now()
        
        if self.retry_count >= self.max_retries:
            self.update_state(ConversationState.MAX_RETRIES_REACHED)
    
    def add_validation_result(self, result: Dict[str, Any]):
        self.validation_history.append({
            'timestamp': datetime.now().isoformat(),
            'retry_count': self.retry_count,
            'result': result
        })
        self.updated_at = datetime.now()
    
    def add_collected_data(self, key: str, value: Any):
        self.collected_data[key] = value
        self.updated_at = datetime.now()
    
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
    
    def can_retry(self) -> bool:
        return self.retry_count < self.max_retries and self.state not in [
            ConversationState.COMPLETED,
            ConversationState.MAX_RETRIES_REACHED
        ]
    
    def get_remaining_retries(self) -> int:
        return max(0, self.max_retries - self.retry_count)
    
    def get_context_summary(self) -> str:
        summary_parts = []
        
        if self.original_input:
            summary_parts.append(f"原始输入：{self.original_input}")
        
        if self.collected_data:
            collected_parts = []
            for key, value in self.collected_data.items():
                collected_parts.append(f"{key}：{value}")
            if collected_parts:
                summary_parts.append(f"已收集信息：{', '.join(collected_parts)}")
        
        if self.retry_count > 0:
            summary_parts.append(f"已尝试次数：{self.retry_count}")
        
        remaining = self.get_remaining_retries()
        if remaining > 0:
            summary_parts.append(f"剩余尝试次数：{remaining}")
        
        return '\n'.join(summary_parts) if summary_parts else "无上下文信息"


class ConversationManager:
    _instance = None
    _conversations: Dict[str, ConversationContext] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def create_conversation(
        self,
        conversation_id: Optional[str] = None,
        user_id: Optional[str] = None,
        original_input: Optional[str] = None,
        max_retries: int = 3
    ) -> ConversationContext:
        if not conversation_id:
            import uuid
            conversation_id = str(uuid.uuid4())
        
        context = ConversationContext(
            conversation_id=conversation_id,
            user_id=user_id,
            original_input=original_input,
            max_retries=max_retries
        )
        self._conversations[conversation_id] = context
        return context
    
    def get_conversation(self, conversation_id: str) -> Optional[ConversationContext]:
        return self._conversations.get(conversation_id)
    
    def update_conversation(
        self,
        conversation_id: str,
        state: Optional[ConversationState] = None,
        collected_data: Optional[Dict[str, Any]] = None
    ) -> Optional[ConversationContext]:
        context = self._conversations.get(conversation_id)
        if not context:
            return None
        
        if state:
            context.update_state(state)
        
        if collected_data:
            for key, value in collected_data.items():
                context.add_collected_data(key, value)
        
        return context
    
    def increment_retry(self, conversation_id: str) -> Optional[ConversationContext]:
        context = self._conversations.get(conversation_id)
        if not context:
            return None
        
        context.increment_retry()
        return context
    
    def add_validation_result(
        self,
        conversation_id: str,
        result: Dict[str, Any]
    ) -> Optional[ConversationContext]:
        context = self._conversations.get(conversation_id)
        if not context:
            return None
        
        context.add_validation_result(result)
        return context
    
    def delete_conversation(self, conversation_id: str) -> bool:
        if conversation_id in self._conversations:
            del self._conversations[conversation_id]
            return True
        return False
    
    def cleanup_expired_conversations(self) -> int:
        current_time = datetime.now()
        expired_ids = []
        
        for conv_id, context in self._conversations.items():
            if context.expires_at and context.expires_at < current_time:
                expired_ids.append(conv_id)
        
        for conv_id in expired_ids:
            del self._conversations[conv_id]
        
        return len(expired_ids)
    
    def get_all_conversations(self) -> Dict[str, ConversationContext]:
        return self._conversations.copy()
    
    def get_conversation_count(self) -> int:
        return len(self._conversations)
    
    def clear_all_conversations(self) -> int:
        count = len(self._conversations)
        self._conversations.clear()
        return count
