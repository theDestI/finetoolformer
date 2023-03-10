import os
from typing import Any
from finetoolformer.tasks.abstract_task import AbstractTask
from finetoolformer.api import call_openai
from finetoolformer.tasks.task_type import TaskType
from finetoolformer.tools import get_assistant_messages

class QnATask(AbstractTask):
    def __init__(self, verbosity=1) -> None:
        super().__init__()
        self.task_description = TaskType.QNA.value
        self.verbosity = verbosity
        self.input_mask = "[INPUT]"
        self.task_prompt = f"""
            Your task is to add calls to a Question Answering API to a piece of text.
            The questions should help you get information required to complete the text. You can call the API by writing
            "[QA(question)]" where "question" is the question you want to ask. Here are some examples of API calls:
            ###
            Input: Joe Biden was born in Scranton, Pennsylvania.
            Output: Joe Biden was born in [QA("Where was Joe Biden born?")] Scranton, [QA("In which state is Scranton?")] Pennsylvania.
            ###
            Input: Coca-Cola, or Coke, is a carbonated soft drink manufactured by the Coca-Cola Company.
            Output: Coca-Cola, or [QA("What other name is Coca-Cola known by?")] Coke, is a carbonated soft drink manufactured by [QA("Who manufactures Coca-Cola?")] the Coca-Cola Company.
            ###
            Input: {self.input_mask}
            Output: [QA("
        """

    def run(self, inquiry:str) -> Any:
        prompt = self.compile_task_prompt(inquiry)

        if self.verbosity > 0:
            print(prompt)

        parameters = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 100,
            "temperature": 1
        }

        text = call_openai(parameters, os.getenv("OPEN_AI_API_TOKEN"))
        text = get_assistant_messages(text.choices)[0].message.content

        return text

    def compile_task_prompt(self, prompt: str) -> str:
        prompt = self.task_prompt.replace(self.input_mask, prompt)

        parameters = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 200,
            "temperature": 1
        }

        task_prompt = call_openai(parameters, os.getenv("OPEN_AI_API_TOKEN"))

        return task_prompt.choices[0].message.content