import google.generativeai as genai
from configparser import ConfigParser


class GeminiModel:
    model = genai.GenerativeModel('gemini-pro')
    config_section = 'geminiApiKey'

    def __init__(self):
        self.get_genai_key()

    def get_genai_key(self):
        parser = ConfigParser()
        parser.read('./app_config.ini')
        if parser.has_section(self.config_section):
            params = parser.items(self.config_section)
            for param in params:
                genai.configure(api_key=param[1])

    def gemini_response_generation(self, prompt):
        response = self.model.generate_content(prompt)
        return response.text
