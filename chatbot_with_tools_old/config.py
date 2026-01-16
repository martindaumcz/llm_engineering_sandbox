"""Configuration module for LLM Chatbot application."""

import os
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv


class Config:
    """Configuration class to manage environment variables and LLM settings."""

    def __init__(self):
        """Initialize configuration by loading environment variables."""
        # Load .env file from the project root
        env_path = Path(__file__).parent.parent / '.env'
        load_dotenv(env_path)

        # API Keys
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        self.deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
        self.xai_api_key = os.getenv('XAI_API_KEY')

        self.default_system_message = "You are a helpful AI assistant."

        # Available LLM Models - Configurable list
        self.available_models = {
            "OpenAI": [
                "gpt-5-mini",
                "gpt-4o-mini"
            ],
            "Anthropic": [
                "claude-haiku-4-5-20251001",
                "claude-sonnet-4-5-20250929",
            ],
            "DeepSeek": [
                "deepseek-chat",
                "deepseek-reasoner"
            ],
            "XAI": [
                "grok-4-fast-reasoning",
                "grok-beta",
                "grok-vision-beta"
            ]
        }

        # Default system message
        self.default_system_message = "You are a helpful AI assistant."

    def get_api_key_by_model(self, model: str):
        return None


    def validate(self) -> bool:
        """Validate that at least one API key is present."""
        if not any([self.openai_api_key, self.anthropic_api_key, self.deepseek_api_key, self.xai_api_key]):
            raise ValueError("No API keys found in .env file. Please provide at least one API key (OPENAI_API_KEY, ANTHROPIC_API_KEY, DEEPSEEK_API_KEY, or XAI_API_KEY)")
        return True

    def get_all_models(self) -> List[str]:
        """Get flat list of all available models with provider prefix."""
        all_models = []
        for provider, models in self.available_models.items():
            for model in models:
                all_models.append(f"{provider}: {model}")
        return all_models

    def parse_model_selection(self, model_string: str) -> Dict[str, str]:
        """Parse model selection string into provider and model name."""
        if ": " in model_string:
            provider, model = model_string.split(": ", 1)
            return {"provider": provider, "model": model}
        return {"provider": "OpenAI", "model": model_string}

    def has_provider_key(self, provider: str) -> bool:
        """Check if API key exists for the given provider."""
        if provider == "OpenAI":
            return self.openai_api_key is not None
        elif provider == "Anthropic":
            return self.anthropic_api_key is not None
        elif provider == "DeepSeek":
            return self.deepseek_api_key is not None
        elif provider == "XAI":
            return self.xai_api_key is not None
        return False


# Global config instance
config = Config()
