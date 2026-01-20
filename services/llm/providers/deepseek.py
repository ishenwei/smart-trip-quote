import aiohttp
import requests
import time
import asyncio
from typing import Optional
from ..base import BaseLLMProvider, LLMRequest, LLMResponse
from ..config import LLMConfig


class DeepSeekProvider(BaseLLMProvider):
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.headers = {
            'Authorization': f'Bearer {config.api_key}',
            'Content-Type': 'application/json'
        }
    
    def validate_config(self) -> bool:
        return bool(self.config.api_key and self.config.api_url)
    
    async def generate(self, request: LLMRequest) -> LLMResponse:
        start_time = time.time()
        
        try:
            messages = self._prepare_messages(request)
            
            payload = {
                'model': self.config.model,
                'messages': messages,
                'temperature': request.temperature or self.config.temperature,
                'max_tokens': request.max_tokens or self.config.max_tokens
            }
            
            if request.additional_params:
                payload.update(request.additional_params)
            
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self.config.api_url,
                    headers=self.headers,
                    json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return LLMResponse(
                            content='',
                            model=self.config.model,
                            provider=self.provider_name,
                            response_time=time.time() - start_time,
                            error=f'HTTP {response.status}: {error_text}'
                        )
                    
                    data = await response.json()
                    
                    content = data['choices'][0]['message']['content']
                    tokens_used = data.get('usage', {}).get('total_tokens')
                    
                    return LLMResponse(
                        content=content,
                        model=self.config.model,
                        provider=self.provider_name,
                        tokens_used=tokens_used,
                        response_time=time.time() - start_time,
                        raw_response=data
                    )
                    
        except asyncio.TimeoutError:
            return LLMResponse(
                content='',
                model=self.config.model,
                provider=self.provider_name,
                response_time=time.time() - start_time,
                error='Request timeout'
            )
        except Exception as e:
            return LLMResponse(
                content='',
                model=self.config.model,
                provider=self.provider_name,
                response_time=time.time() - start_time,
                error=str(e)
            )
    
    def generate_sync(self, request: LLMRequest) -> LLMResponse:
        start_time = time.time()
        
        try:
            messages = self._prepare_messages(request)
            
            payload = {
                'model': self.config.model,
                'messages': messages,
                'temperature': request.temperature or self.config.temperature,
                'max_tokens': request.max_tokens or self.config.max_tokens
            }
            
            if request.additional_params:
                payload.update(request.additional_params)
            
            response = requests.post(
                self.config.api_url,
                headers=self.headers,
                json=payload,
                timeout=self.config.timeout
            )
            
            if response.status_code != 200:
                return LLMResponse(
                    content='',
                    model=self.config.model,
                    provider=self.provider_name,
                    response_time=time.time() - start_time,
                    error=f'HTTP {response.status_code}: {response.text}'
                )
            
            data = response.json()
            
            content = data['choices'][0]['message']['content']
            tokens_used = data.get('usage', {}).get('total_tokens')
            
            return LLMResponse(
                content=content,
                model=self.config.model,
                provider=self.provider_name,
                tokens_used=tokens_used,
                response_time=time.time() - start_time,
                raw_response=data
            )
            
        except requests.exceptions.Timeout:
            return LLMResponse(
                content='',
                model=self.config.model,
                provider=self.provider_name,
                response_time=time.time() - start_time,
                error='Request timeout'
            )
        except Exception as e:
            return LLMResponse(
                content='',
                model=self.config.model,
                provider=self.provider_name,
                response_time=time.time() - start_time,
                error=str(e)
            )
