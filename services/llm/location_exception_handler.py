from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
import uuid
import json

from .location_validator import LocationValidator, LocationValidationResult, LocationValidationStatus
from .conversation_manager import ConversationManager, ConversationContext, ConversationState
from .logger import LLMLogger


@dataclass
class LocationExceptionHandlerResult:
    success: bool
    should_continue: bool
    user_message: Optional[str] = None
    enhanced_prompt: Optional[str] = None
    conversation_id: Optional[str] = None
    retry_count: int = 0
    original_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    suggestions: Optional[list] = None


class LocationExceptionHandler:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.conversation_manager = ConversationManager()
        self.logger = LLMLogger()
        self.max_retries = 3
    
    def handle_location_validation(
        self,
        user_input: str,
        llm_response_data: Dict[str, Any],
        conversation_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> LocationExceptionHandlerResult:
        validation_result = LocationValidator.validate_locations(llm_response_data)
        
        if validation_result.is_valid:
            self._log_validation_success(conversation_id, user_input, validation_result)
            
            if conversation_id:
                context = self.conversation_manager.get_conversation(conversation_id)
                if context:
                    context.update_state(ConversationState.COMPLETED)
                    self.conversation_manager.update_conversation(conversation_id, state=ConversationState.COMPLETED)
            
            return LocationExceptionHandlerResult(
                success=True,
                should_continue=True,
                original_data=llm_response_data,
                conversation_id=conversation_id,
                retry_count=0
            )
        
        return self._handle_validation_failure(
            user_input,
            validation_result,
            conversation_id,
            user_id,
            llm_response_data
        )
    
    def _handle_validation_failure(
        self,
        user_input: str,
        validation_result: LocationValidationResult,
        conversation_id: Optional[str],
        user_id: Optional[str],
        original_data: Dict[str, Any]
    ) -> LocationExceptionHandlerResult:
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
            self.conversation_manager.create_conversation(
                conversation_id=conversation_id,
                user_id=user_id,
                original_input=user_input,
                max_retries=self.max_retries
            )
        
        context = self.conversation_manager.get_conversation(conversation_id)
        if not context:
            return LocationExceptionHandlerResult(
                success=False,
                should_continue=False,
                error="无法创建或获取对话上下文"
            )
        
        context.add_validation_result({
            'status': validation_result.status.value,
            'error_message': validation_result.error_message,
            'origin': validation_result.origin,
            'destination': validation_result.destination
        })
        
        context.increment_retry()
        
        self._log_validation_failure(conversation_id, user_input, validation_result, context.retry_count)
        
        if not context.can_retry():
            return self._handle_max_retries_reached(context, user_input, validation_result)
        
        user_friendly_message = LocationValidator.generate_user_friendly_message(validation_result, user_input)
        enhanced_prompt = self._generate_enhanced_prompt(user_input, validation_result, context)
        
        return LocationExceptionHandlerResult(
            success=False,
            should_continue=True,
            user_message=user_friendly_message,
            enhanced_prompt=enhanced_prompt,
            conversation_id=conversation_id,
            retry_count=context.retry_count,
            original_data=original_data,
            suggestions=validation_result.suggestions
        )
    
    def _handle_max_retries_reached(
        self,
        context: ConversationContext,
        user_input: str,
        validation_result: LocationValidationResult
    ) -> LocationExceptionHandlerResult:
        context.update_state(ConversationState.MAX_RETRIES_REACHED)
        
        error_message = f"抱歉，经过{context.retry_count}次尝试后，仍无法识别您的位置信息。\n\n"
        error_message += "您的原始输入：{user_input}\n\n"
        error_message += "请参考以下示例重新描述您的需求：\n\n"
        
        examples = LocationValidator.get_input_examples()
        for i, example in enumerate(examples, 1):
            error_message += f"{i}. {example}\n"
        
        error_message += "\n或者您可以选择：\n"
        error_message += "• 重新开始对话\n"
        error_message += "• 联系客服获取帮助"
        
        self._log_max_retries_reached(context.conversation_id, user_input, context.retry_count)
        
        return LocationExceptionHandlerResult(
            success=False,
            should_continue=False,
            user_message=error_message,
            conversation_id=context.conversation_id,
            retry_count=context.retry_count,
            original_data=None,
            error="达到最大重试次数"
        )
    
    def _generate_enhanced_prompt(
        self,
        original_input: str,
        validation_result: LocationValidationResult,
        context: ConversationContext
    ) -> str:
        enhanced_prompt = f"用户原始输入：{original_input}\n\n"
        
        if context.original_input:
            enhanced_prompt += f"对话上下文：\n{context.get_context_summary()}\n\n"
        
        enhanced_prompt += "系统反馈：\n"
        enhanced_prompt += f"状态：{validation_result.status.value}\n"
        enhanced_prompt += f"错误：{validation_result.error_message}\n\n"
        
        if validation_result.status == LocationValidationStatus.MISSING_BOTH:
            enhanced_prompt += "请用户同时提供出发地和目的地信息。\n"
            enhanced_prompt += "示例格式：'从[出发地]去[目的地]'\n"
        
        elif validation_result.status == LocationValidationStatus.MISSING_ORIGIN:
            dest_name = self._extract_destination_name(validation_result.destination)
            enhanced_prompt += f"目的地已识别为'{dest_name}'，但缺少出发地信息。\n"
            enhanced_prompt += "请用户说明从哪个城市出发。\n"
            enhanced_prompt += "示例格式：'从[出发地]出发'\n"
        
        elif validation_result.status == LocationValidationStatus.MISSING_DESTINATION:
            origin_name = validation_result.origin.get('name', '未知')
            enhanced_prompt += f"出发地已识别为'{origin_name}'，但缺少目的地信息。\n"
            enhanced_prompt += "请用户说明想去哪个城市。\n"
            enhanced_prompt += "示例格式：'去[目的地]'\n"
        
        enhanced_prompt += f"\n当前尝试次数：{context.retry_count}/{context.max_retries}\n"
        enhanced_prompt += "剩余尝试次数：{}\n".format(context.get_remaining_retries())
        
        enhanced_prompt += "\n请根据以上反馈，重新分析用户的旅游需求，"
        enhanced_prompt += "重点关注地理位置信息的提取。"
        
        return enhanced_prompt
    
    def _extract_destination_name(self, destinations: Optional[list]) -> str:
        if not destinations:
            return "未知"
        
        for dest in destinations:
            if isinstance(dest, dict):
                name = dest.get('name')
                if name and LocationValidator._is_valid_location_name(name):
                    return name
        
        return "未知"
    
    def _log_validation_success(
        self,
        conversation_id: Optional[str],
        user_input: str,
        validation_result: LocationValidationResult
    ):
        log_data = {
            'conversation_id': conversation_id,
            'user_input': user_input,
            'validation_status': validation_result.status.value,
            'origin': validation_result.origin,
            'destination': validation_result.destination
        }
        
        self.logger._logger.info(f"Location Validation Success: {json.dumps(log_data, ensure_ascii=False)}")
    
    def _log_validation_failure(
        self,
        conversation_id: str,
        user_input: str,
        validation_result: LocationValidationResult,
        retry_count: int
    ):
        log_data = {
            'conversation_id': conversation_id,
            'user_input': user_input,
            'validation_status': validation_result.status.value,
            'error_message': validation_result.error_message,
            'origin': validation_result.origin,
            'destination': validation_result.destination,
            'retry_count': retry_count
        }
        
        self.logger._logger.warning(f"Location Validation Failed: {json.dumps(log_data, ensure_ascii=False)}")
    
    def _log_max_retries_reached(
        self,
        conversation_id: str,
        user_input: str,
        retry_count: int
    ):
        log_data = {
            'conversation_id': conversation_id,
            'user_input': user_input,
            'retry_count': retry_count,
            'max_retries': self.max_retries
        }
        
        self.logger._logger.error(f"Max Retries Reached: {json.dumps(log_data, ensure_ascii=False)}")
    
    def get_conversation_context(self, conversation_id: str) -> Optional[ConversationContext]:
        return self.conversation_manager.get_conversation(conversation_id)
    
    def cleanup_expired_conversations(self) -> int:
        count = self.conversation_manager.cleanup_expired_conversations()
        if count > 0:
            self.logger._logger.info(f"Cleaned up {count} expired conversations")
        return count
    
    def get_statistics(self) -> Dict[str, Any]:
        total_conversations = self.conversation_manager.get_conversation_count()
        active_conversations = 0
        completed_conversations = 0
        failed_conversations = 0
        
        for context in self.conversation_manager.get_all_conversations().values():
            if context.state == ConversationState.COMPLETED:
                completed_conversations += 1
            elif context.state == ConversationState.MAX_RETRIES_REACHED:
                failed_conversations += 1
            else:
                active_conversations += 1
        
        return {
            'total_conversations': total_conversations,
            'active_conversations': active_conversations,
            'completed_conversations': completed_conversations,
            'failed_conversations': failed_conversations,
            'success_rate': round(completed_conversations / total_conversations * 100, 2) if total_conversations > 0 else 0
        }
