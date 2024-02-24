import openai
import os
import tiktoken

API_KEY = ""
os.environ["OPEN_API_KEY"] = API_KEY

openai.api_key = os.getenv("GEMINI_API_KEY")


class GPTModel:
    def __init__(self):
        self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo-0613")
        self.num_tokens = 0
        self.token_pricing = 0.0005
        self.max_ans_len = 600
        self.no_of_prompt = 0
        self.total_tokens = 0

    def calculate_no_of_tokens(self, prompt):
        self.num_tokens += len(self.encoding.encode(prompt))
        self.no_of_prompt += 1

    def calculate_cost(self):
        self.total_tokens = (self.no_of_prompt * self.max_ans_len) + self.num_tokens
        cost = (self.token_pricing * self.total_tokens) / 1000

        return cost

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
