import aiohttp
import requests
import time
import asyncio
from typing import Optional
from ..base import BaseLLMProvider, LLMRequest, LLMResponse
from ..config import LLMConfig


class GeminiProvider(BaseLLMProvider):
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.api_key = config.api_key
        self.api_url = config.api_url
    
    def validate_config(self) -> bool:
        return bool(self.config.api_key and self.config.api_url)
    
    def _prepare_gemini_request(self, request: LLMRequest) -> dict:
        contents = []
        
        if request.system_prompt:
            contents.append({
                'role': 'user',
                'parts': [{'text': f"System: {request.system_prompt}"}]
            })
        
        contents.append({
            'role': 'user',
            'parts': [{'text': request.prompt}]
        })
        
        return {
            'contents': contents,
            'generationConfig': {
                'temperature': request.temperature or self.config.temperature,
                'maxOutputTokens': request.max_tokens or self.config.max_tokens
            }
        }
    
    async def generate(self, request: LLMRequest) -> LLMResponse:
        start_time = time.time()
        
        try:
            url = f"{self.api_url}?key={self.api_key}"
            payload = self._prepare_gemini_request(request)
            
            if request.additional_params:
                payload['generationConfig'].update(request.additional_params)
            
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    url,
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
                    
                    if 'candidates' not in data or not data['candidates']:
                        return LLMResponse(
                            content='',
                            model=self.config.model,
                            provider=self.provider_name,
                            response_time=time.time() - start_time,
                            error='No candidates in response'
                        )
                    
                    content = data['candidates'][0]['content']['parts'][0]['text']
                    tokens_used = data.get('usageMetadata', {}).get('totalTokenCount')
                    
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
            url = f"{self.api_url}?key={self.api_key}"
            payload = self._prepare_gemini_request(request)
            
            if request.additional_params:
                payload['generationConfig'].update(request.additional_params)
            
            response = requests.post(
                url,
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
            
            if 'candidates' not in data or not data['candidates']:
                return LLMResponse(
                    content='',
                    model=self.config.model,
                    provider=self.provider_name,
                    response_time=time.time() - start_time,
                    error='No candidates in response'
                )
            
            content = data['candidates'][0]['content']['parts'][0]['text']
            tokens_used = data.get('usageMetadata', {}).get('totalTokenCount')
            
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
