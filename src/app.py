from fastapi import FastAPI

import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


app = FastAPI()


def openai_chat_completion(question, model="gpt-3.5-turbo"):
    completion = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a funny assistant."},
            {"role": "user", "content": question},
        ],
    )
    return completion.choices[0].message["content"]


@app.get("/")
def root():
    return {"Hello": "World"}


@app.get("/qa")
def qa(question: str):
    answer = openai_chat_completion(question)
    return {"question": question, "answer": answer}
