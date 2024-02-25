import openai
import os
from configparser import ConfigParser


class GPTModel:
    config_section = 'openAIKey'
    open_ai_key = None
    model_name = None

    def __init__(self, model):
        if model == "gpt":
            self.model_name = "gpt-3.5-turbo-0125"

        elif model == "gpt4":
            self.model_name = "gpt-4"

        self.get_openai_key()

    def get_openai_key(self):
        parser = ConfigParser()
        parser.read('./app_config.ini')
        if parser.has_section(self.config_section):
            params = parser.items(self.config_section)
            for param in params:
                self.open_ai_key = param[1]

    def gpt_response_generation(self, prompt):
        response = openai.ChatCompletion.create(
            model= self.model_name,
            messages=[{"role": "user", "content": prompt}],
            api_key=self.open_ai_key,
            n=1,
            stream=False,
            temperature=0.2,
            max_tokens=600,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop=["Q:"]
        )

        output = response['choices'][0]['message']['content']
        try:
            if output.index("SELECT") > -1:
                output = output.replace("SELECT", "", 1).strip()

            if output.index("```sql") > -1:
                output = output.replace("sql", "").replace("`", "").strip()

            output.replace(";", "").replace("` ", "").replace("`", "").strip()
        except ValueError as ex:
            return output

        return output

    def gpt_debug_response_generation(self, prompt):
        response = openai.ChatCompletion.create(
            model= self.model_name,
            messages=[{"role": "user", "content": prompt}],
            api_key=self.open_ai_key,
            n=1,
            stream=False,
            temperature=0.2,
            max_tokens=350,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop=["#", ";", "\n\n"]
        )

        output = response['choices'][0]['message']['content']
        try:
            if output.index("SELECT") > -1:
                output = output.replace("SELECT", "", 1).strip()

            if output.index("```sql") > -1:
                output = output.replace("sql", "").replace("`", "").strip()

            output.replace(";", "").replace("` ", "").replace("`", "").strip()
        except ValueError as ex:
            return output

        return output
