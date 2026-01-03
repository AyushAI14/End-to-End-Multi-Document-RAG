import os
import sys
from dotenv import load_dotenv

from multi_doc_chat.utils.config_loaders import load_config
from langchain_google_genai import (
    GoogleGenerativeAIEmbeddings,
    ChatGoogleGenerativeAI,
)
from langchain_groq import ChatGroq
from multi_doc_chat.logger import log
from multi_doc_chat.exception.customException import DocumentPortalException

load_dotenv()


class ModelLoader:
    """
    Loads embedding models and LLMs from config
    """

    def __init__(self):
        self.config = load_config()
        log.info(f"Config Yaml loaded : {list(self.config.keys())}")

        # 🔑 HARD NORMALIZATION (critical)
        api_key = (
            os.getenv("GOOGLE_API_KEY")
            or os.getenv("GEMINI_API_KEY")
        )

        if not api_key:
            raise RuntimeError(
                "Missing GOOGLE_API_KEY / GEMINI_API_KEY in environment"
            )

        # Force SDK to see it
        os.environ["GOOGLE_API_KEY"] = api_key

    def load_embedding(self):
        """
        Load and return embedding model
        """
        try:
            model_name = self.config["embedding_model"]["model_name"]

            embedding = GoogleGenerativeAIEmbeddings(
                model=model_name
            )

            return embedding

        except Exception as e:
            log.error("Error loading embedding model", error=str(e))
            raise DocumentPortalException(
                "Failed to load embedding model", sys
            )

    def load_llm(self):
        """
        Load and return LLM
        """
        llm_section = self.config["llm"]
        provider_key = "google"

        if provider_key not in llm_section:
            raise ValueError(f"LLM provider '{provider_key}' not found")

        llm_config = llm_section[provider_key]

        provider = llm_config.get("provider")
        model_name = llm_config.get("model_name")
        temperature = llm_config.get("temperature", 0.2)
        max_tokens = llm_config.get("max_output_tokens", 2048)

        log.info("Loading LLM", provider=provider, model=model_name)

        if provider == "google":
            return ChatGoogleGenerativeAI(
                model=model_name,
                temperature=temperature,
                max_output_tokens=max_tokens,
            )

        elif provider == "groq":
            return ChatGroq(
                model=model_name,
                api_key=os.getenv("GROQ_API_KEY"),
                temperature=temperature,
            )

        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
