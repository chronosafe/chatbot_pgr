import openai
import langchain

class LangChainProvider:
    def __init__(self, api_key):
        openai.api_key = api_key
    
    def generate(self, prompt):
        response = openai.Completion.create(
            engine="davinci",
            prompt=prompt,
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.5,
        )
        return response.choices[0].text.strip()

class ChatBot:
    def __init__(self, provider):
        self.prompt = ""
        self.provider = provider
    
    def query(self, prompt):
        response = self.provider.generate(prompt)
        self.prompt = prompt
        return response