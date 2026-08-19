"""
core/llm_wrapper.py

One class every module calls instead of hitting an SDK directly.
Swapping providers (Gemini <-> OpenAI) means changing one argument here,
not touching any of the 7 module pages. This is what satisfies the
"multi-model support" bonus point with almost no extra code.

Usage:
    from core.llm_wrapper import LLMWrapper
    llm = LLMWrapper(provider="gemini")          # or "openai"
    text = llm.generate("Explain RAG in 2 lines")
    for chunk in llm.generate_stream("Write a haiku about caches"):
        ...
"""

import os
from dotenv import load_dotenv

load_dotenv()


class LLMWrapper:
    def __init__(self, provider: str = "gemini", model: str | None = None):
        self.provider = provider
        if provider == "gemini":
            import google.generativeai as genai

            genai.configure(api_key=os.environ["GEMINI_API_KEY"])
            # llm_wrapper.py
            self.model_name = model or os.environ.get("GEMINI_MODEL", "gemini-3.6-flash")
            self._client = genai.GenerativeModel(self.model_name)
        elif provider == "openai":
            from openai import OpenAI

            self._client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
            self.model_name = model or "gpt-4o-mini"
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def generate(self, prompt: str, system: str | None = None) -> str:
        """Non-streaming call. Good for short structured outputs (e.g. JSON extraction)."""
        full_prompt = f"{system}\n\n{prompt}" if system else prompt

        if self.provider == "gemini":
            response = self._client.generate_content(full_prompt)
            return response.text

        if self.provider == "openai":
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            response = self._client.chat.completions.create(
                model=self.model_name, messages=messages
            )
            return response.choices[0].message.content

    def generate_stream(self, prompt: str, system: str | None = None):
        """Yields text chunks. Feed directly into st.write_stream()."""
        full_prompt = f"{system}\n\n{prompt}" if system else prompt

        if self.provider == "gemini":
            response = self._client.generate_content(full_prompt, stream=True)
            for chunk in response:
                if chunk.text:
                    yield chunk.text

        elif self.provider == "openai":
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            stream = self._client.chat.completions.create(
                model=self.model_name, messages=messages, stream=True
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta