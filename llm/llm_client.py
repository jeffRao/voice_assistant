"""大模型调用模块"""
from typing import Iterator, Optional, List, Dict, Any
from openai import OpenAI


class LLMClient:
    """大模型客户端"""
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.openai.com/v1",
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.kwargs = kwargs
        
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        stream: bool = True
    ) -> Iterator[str]:
        """流式对话
        
        Args:
            messages: 消息列表
            stream: 是否使用流式返回
            
        Yields:
            生成的文本片段
        """
        try:
            stream_in_args = self.kwargs.pop("stream", True)
            if stream is None:
                stream = stream_in_args
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=stream,
                **self.kwargs
            )
            
            if stream:
                for chunk in response:
                    if chunk.choices and len(chunk.choices) > 0:
                        delta = chunk.choices[0].delta
                        if hasattr(delta, 'content') and delta.content:
                            yield delta.content
            else:
                if response.choices and len(response.choices) > 0:
                    yield response.choices[0].message.content
                    
        except Exception as e:
            print(f"大模型调用失败: {e}")
            yield f"[错误: {str(e)}]"
    
    def simple_chat(self, user_message: str, system_prompt: Optional[str] = None) -> Iterator[str]:
        """简单对话
        
        Args:
            user_message: 用户消息
            system_prompt: 系统提示词
            
        Yields:
            生成的文本片段
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": user_message})
        
        yield from self.chat(messages, stream=True)
