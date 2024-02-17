import openai
import os

API_KEY = ""
os.environ["OPEN_API_KEY"] = API_KEY

openai.api_key = os.getenv("GEMINI_API_KEY")


class GPTModel:
    def __init__(self):
        pass

    @staticmethod
    def gpt_response_generation(self, prompt):
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            n=1,
            stream=False,
            temperature=0.0,
            max_tokens=600,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop=["Q:"]
        )
        return response['choices'][0]['message']['content']

    @staticmethod
    def gpt_debug(self, prompt):
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            n=1,
            stream=False,
            temperature=0.0,
            max_tokens=350,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop=["#", ";", "\n\n"]
        )
        return response['choices'][0]['message']['content']

