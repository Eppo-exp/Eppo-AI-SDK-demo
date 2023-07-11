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

Next, install the libraries we will use using
```
pip install -r requirements.txt
```
Now start the app using
```
uvicorn src.app:app --reload
```

Navigate to `http://127.0.0.1:8000/` and verify that the app indeed returns `{"Hello":"World"}`
