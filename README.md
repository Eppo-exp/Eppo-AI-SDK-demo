# Eppo AI SDK Demo

This is a simple end-to-end example of how to run an experiment on LLMs. We will be using:

- FastAPI to create a simple webserver
- Eppo's Python SDK to fetch feature flag configuration
- OpenAI API to answer questions

## Getting started

Create a virtual environment, e.g. if you use `virtualenv` then you can use

```
pyenv virtualenv <python-version> eppo-ai-sdk-demo
```

and activate it

```
pyenv activate eppo-ai-sdk-demo
```

Note, use `python versions` to list available versions and select the version you want to use (e.g. `3.10.6`, assuming you have that version installed).

Next, install the libraries we will use using

```
pip install -r requirements.txt
```

We create a simple Hello World API as follows in `src/app.py`:

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {"Hello": "World"}
```

Now start the app using

```
uvicorn src.app:app --reload
```

Navigate to `http://127.0.0.1:8000/` and verify that the app indeed returns `{"Hello":"World"}`.
Furthermore, you can navigate to `http://127.0.0.1:8000/docs` to see the interactive documentation that is automatically generated.
We will leverage these docs to interact and test our application moving forward.

## Creating a QA endpoint

Next up, let's create an endpoint that can answer questions.
First, set up the API endpoint by adding the following endpoint:

```python
@app.get("/qa")
def qa(question: str):
    return {"question": question, "answer": "42"}
```

Now use the interactive docs or navigate to `http://127.0.0.1:8000/qa?question=What%20is%20the%20answer%20to%20the%20ultimate%20question%20of%20life%3F` to verify everything works as expected.

### Integrating the OpenAI API

Let's make things a bit more interesting by integrating with the OpenAI API to help us answer questions.
Make sure you have signed up for the [OpenAI API](https://openai.com/blog/openai-api) and have an OpenAI API key.

Let's store the API key locally and make sure it does not get checked into github by accident.
Copy the `.env.dist` file to `.env` from the top-level directory like so:

```
cp src/.env.dist src/.env
```

Now open `src/.env` and add your OpenAI API key.

Next, we install the `openai` and `python-dotenv` libraries (the latter is used to read the API key you just stored).

Add the following to the top of your app.py file:

```python
import os
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

print(openai.api_key[:6]) # optional to test you indeed loaded your API key successfully
```

For the fun part, we create a function that uses OpenAI's chat completion to answer our question by adding the following code

```python
def openai_chat_completion(question, model="gpt-3.5-turbo"):
    completion = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a funny assistant."},
            {"role": "user", "content": question},
        ],
    )
    return completion.choices[0].message["content"]
```

and update our `qa` endpoint to use this function:

```python
@app.get("/qa")
def qa(question: str):
    answer = openai_chat_completion(question)
    return {"question": question, "answer": answer}
```

Test the endpoint again and verify that the answer to the ultimate question of life got slightly longer.
