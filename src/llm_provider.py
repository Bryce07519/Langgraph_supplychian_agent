# src/llm_provider.py
import os
import requests
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models import ChatOllama
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_core.runnables import RunnableBinding
from typing import List, Dict, Any, Optional, Union, Type


class CustomAPIChatModel(BaseChatModel):
    """Custom chat model that connects to a local API endpoint."""
    
    api_url: str = "http://124.223.22.249:6399/v1/chat/completions"
    model_name: str = "deepseek-v3"
    temperature: float = 0.7
    max_tokens: int = 2048
    
    def __init__(self, api_url: Optional[str] = None, model_name: Optional[str] = None, 
                 temperature: float = 0.7, max_tokens: int = 2048, **kwargs):
        super().__init__(**kwargs)
        if api_url:
            self.api_url = api_url
        if model_name:
            self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    @property
    def _llm_type(self) -> str:
        return "custom_api_chat_model"
    
    def _generate(self, messages: List, stop: Optional[List[str]] = None, **kwargs) -> ChatResult:
        headers = {
            "Content-Type": "application/json"
        }
        
        # Convert LangChain messages to the format expected by the API
        api_messages = []
        for message in messages:
            if isinstance(message, SystemMessage):
                api_messages.append({"role": "system", "content": message.content})
            elif isinstance(message, HumanMessage):
                api_messages.append({"role": "user", "content": message.content})
            elif isinstance(message, AIMessage):
                api_messages.append({"role": "assistant", "content": message.content})
        
        payload = {
            "model": self.model_name,
            "messages": api_messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            
            response.raise_for_status()
            response_data = response.json()
            
            # Extract the assistant's message from the response
            assistant_message = response_data['choices'][0]['message']['content']
            
            # Create a ChatGeneration object
            generation = ChatGeneration(
                message=AIMessage(content=assistant_message),
                text=assistant_message
            )
            
            # Return a ChatResult object
            return ChatResult(generations=[generation])
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {e}")
        except (KeyError, IndexError, TypeError) as e:
            raise Exception(f"Failed to parse API response: {e}. Response content: {response.text if 'response' in locals() else 'No response'}")
 
    def with_structured_output(
        self, 
        schema: Union[Dict, Type], 
        **kwargs: Any
    ) -> RunnableBinding:
        """为CustomAPIChatModel添加结构化输出支持
        
        Args:
            schema: 用于结构化输出的模式，可以是Pydantic模型或字典
            **kwargs: 其他参数
            
        Returns:
            RunnableBinding: 绑定结构化输出的可运行对象
        """
        # 直接返回self，因为我们会在graph_nodes.py中手动处理结构化输出
        # 这样可以避免NotImplementedError错误
        return self


def get_llm(provider: str, model: str = None):
    """
    根据提供的provider获取LLM实例。
    """
    if provider.lower() == 'openai':
        model = model or "gpt-4-turbo-preview"
        return ChatOpenAI(model=model, temperature=0)
    elif provider.lower() == 'gemini':
        model = model or "gemini-2.5-flash"
        return ChatGoogleGenerativeAI(model=model, temperature=0, convert_system_message_to_human=True)
    elif provider.lower() == 'deepseek':
        # 假设通过Ollama运行deepseek-coder或类似模型
        model = model or "deepseek-coder" 
        return ChatOllama(model=model, base_url=os.getenv("OLLAMA_BASE_URL"))
    elif provider.lower() == 'local':
        # 支持本地API接口
        api_url = os.getenv("LOCAL_LLM_API_URL", "http://124.223.22.249:6399/v1/chat/completions")
        model_name = model or os.getenv("LOCAL_LLM_MODEL_NAME", "deepseek-v3")
        return CustomAPIChatModel(api_url=api_url, model_name=model_name, temperature=0)
    else:
        raise ValueError(f"不支持的 LLM provider: {provider}")


def get_fast_llm(provider: str):
    """获取一个速度更快、成本更低的模型用于分类等简单任务"""
    if provider.lower() == 'openai':
        return ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    elif provider.lower() == 'local':
        # For local provider, use the same model but with a higher temperature for faster responses
        api_url = os.getenv("LOCAL_LLM_API_URL", "http://124.223.22.249:6399/v1/chat/completions")
        model_name = os.getenv("LOCAL_LLM_MODEL_NAME", "deepseek-v3")
        return CustomAPIChatModel(api_url=api_url, model_name=model_name, temperature=0)
    # 对于其他提供商，可以返回同样模型或指定一个更快的版本
    return get_llm(provider)