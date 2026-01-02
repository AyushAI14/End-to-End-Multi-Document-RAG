import os
import sys
import json
from dotenv import load_dotenv
from multi_doc_chat.utils.config_loaders import load_config
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from multi_doc_chat.logger import  log
from multi_doc_chat.exception.customException import DocumentPortalException
load_dotenv()

class ModelLoader:
    """
    Loads embedding models and llms from config 
    """
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.config = load_config()
        log.info(f'Config Yaml loaded : {list(self.config.keys())}')
    
    def load_embedding(self):
        """
        This load and return embedding of words
        """
        try:
            model_name = self.config['embedding_model']['model_name']
            embedding = GoogleGenerativeAIEmbeddings(model = model_name,api_key= self.api_key)
            return embedding
            
        except Exception as e:
                    log.error("Error loading embedding model", error=str(e))
                    raise DocumentPortalException("Failed to load embedding model", sys)
                    
    def load_llm(self):
        """
        Load and return the config model
        """
        llm_section = self.config['llm']
        provider_key  = 'google'
        if provider_key not in llm_section:
            log.error("LLM provider not found in config", provider=provider_key)
            raise ValueError(f"LLM provider '{provider_key}' not found in config")
        
        llm_config = llm_section[provider_key]
        provider = llm_config.get("provider")
        model_name = llm_config.get("model_name")
        temperature = llm_config.get("temperature", 0.2)
        max_tokens = llm_config.get("max_output_tokens", 2048)

        log.info("Loading LLM", provider=provider, model=model_name)
        
        if provider == "google":
                    return ChatGoogleGenerativeAI(
                        model=model_name,
                        google_api_key=os.getenv("GEMINI_API_KEY"),
                        temperature=temperature,
                        max_output_tokens=max_tokens
                    )
        
        elif provider == "groq":
            return ChatGroq(
                model=model_name,
                api_key=os.getenv("GROQ_API_KEY"), #type: ignore
                temperature=temperature,
            )

        else:
            log.error("Unsupported LLM provider", provider=provider)
            raise ValueError(f"Unsupported LLM provider: {provider}")

if __name__ == '__main__':
    loader = Modelloader()
    # Test Embedding
    # embeddings = loader.load_embedding()
    # print(f"Embedding Model Loaded: {embeddings}")
    # result = embeddings.embed_query("Hello, how are you?")
    # print(f"Embedding Result: {result}")

    # Test LLM
    llm = loader.load_llm()
    print(f"LLM Loaded: {llm}")
    result = llm.invoke("Hello, how are you?")
    print(f"LLM Result: {result.content}")