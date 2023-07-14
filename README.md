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

## Creating an experiment

We now have a new way to answer questions, but how can we verify that our users prefer this option?
Of course, we can run an experiment: we randomize users into different variations and then analyze the outcomes on key metrics we care about.
Let's integrate the Eppo feature flagging SDK to make this trivial.

### Creating an API key

First, create an [Eppo API key](https://docs.geteppo.com/feature-flag-quickstart) in the test environment.
The name is unimporant, consider calling it `AI testing key`, but make sure you copy paste the actual key into the your `src/.env` file.
For the correct format, compare your `.env` file with the `.env.dist` file.

![Creating an API key](https://docs.geteppo.com/assets/images/api-key-739caaf4a3acdea7ba9c56f1603592f4.png)

### Setting up a feature flag

With the API key setup, we can now create a feature flag and evaluate it in our app.
Create a new feature flag called `AI demo model version` and we can use the automatically generated key `ai-demo-model-version`.
Let's create three variations:

- GPT3.5
- GPT4
- Fixed (for always responding with the answer `42`)

![Create feature flag](/static/img/create-feature-flag.png)

Then, create an _allocation_, which determines how the flag gets triggered.
For an experiment, we might want to randomize users into each of the 3 variants with equal probability

![Create allocation](/static/img/experiment_allocation.png)

Finally, turn on the flag in the testing environment so that we can evaluate it in our app.
Your setup should now look like

![Feature flag configuration](/static/img/feature_flag_overview.png)

### Adding the feature flag to the app

First up, install the Eppo Python SDK using `pip install eppo-server-sdk`.
We should now be able to import the SDK into our script by adding

```python
import eppo_client
from eppo_client.config import Config
from eppo_client.assignment_logger import AssignmentLogger
```

to our imports.

Next, we set up our logger and initialize the SDK client, which fetches the allocation configuration we just set up in the Eppo UI

```python
class PrintAssignment(AssignmentLogger):
    def log_assignment(self, assignment):
        print(assignment)


client_config = Config(
    api_key=os.getenv("EPPO_API_KEY"), assignment_logger=PrintAssignment()
)
eppo = eppo_client.get_instance()
```

In practice, you want to set up the logger to write the assignments to an assignment table in your data warehouse so that we can analyze the outcomes of the experiment by joining these assignments to the metrics we care about.
But for now, printing the assignment is a useful placeholder to make sure everything works locally.

Next, let's tweak our QA endpoint to fetch the variant. We make three simple changes:

- Add a user argument to the endpoint: randomization happens based on a key (usually a `user_id`) so that we can ensure the same user sees a consistent experience throughout the experiment. Thus, the randomizer needs to know what user hits the endpoint.
- We fetch the variant from the randomizer
- We add the variant to the response, so that we can conveniently inspect the results

```python
@app.get("/qa")
def qa(user: str, question: str):
    variant = eppo.get_assignment(user, "ai-demo-model-version")
    answer = openai_chat_completion(question)
    return {"question": question, "answer": answer, "variant": variant}
```

Note that we have not updated the completion code yet; first let's focus on making sure we integrated the SDK successfully.
Test the endpoint either through the interactive docs or browsing directly to these URLs:

- http://127.0.0.1:8000/qa?user=Alice&question=What%27s%20the%20answer%20to%20the%20ultimate%20question%20of%20life
- http://127.0.0.1:8000/qa?user=Bob&question=What%27s%20the%20answer%20to%20the%20ultimate%20question%20of%20life
- http://127.0.0.1:8000/qa?user=Charlie&question=What%27s%20the%20answer%20to%20the%20ultimate%20question%20of%20life

Make sure to try the same user a couple of times to verify that indeed the exact same variant shows up every time. In my case, Alice and Bob consistently see the GPT4 variant, while Charlie sees GPT3.5, but you will see different results.
Furthermore, you should see the assignments log to your terminal as well:

```
{'experiment': 'ai-demo-model-version', 'variation': 'gpt-4', 'subject': 'Alice', 'timestamp': '2023-07-14T18:21:18.363098', 'subjectAttributes': {}}
```

### Putting the flag to action

We saved the best for last: using our variant to dynamically pick model version.
This is now a simple change to our `qa` endpoint.

When `"gpt"` is in the variant name, we can supply the model variant directly to the `openai_chat_completion` function.
Otherwise, simply return `"42"`.
Note that it is good practice to code defensively here.
While the Eppo SDK is extremely robust, by checking whether the variant actually exists we make sure the code runs correctly even when there is an issue fetching the assignment from our SDK.

```python
@app.get("/qa")
def qa(user: str, question: str):
    variant = eppo.get_assignment(user, "ai-demo-model-version")
    if variant and "gpt" in variant:
        answer = openai_chat_completion(question, model=variant)
    else:
        answer = "42"
    return {"question": question, "answer": answer, "variant": variant}
```

Using either the URLs above or the interactive documentation, we can now verify that the variant assigned to different users indeed leads to the API returning different endpoints.
