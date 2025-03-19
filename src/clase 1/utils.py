import dotenv
import os
import getpass


def load_api_key():
    """Function to load the API from .env"""
    dotenv.load_dotenv()

    if not os.environ.get("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = getpass.getpass(f"Enter API key for OpenAI: ")


def streaming_print(llm, query):
    """Function to print the stream of the LLM"""
    for chunk in llm.stream(query):
        print(chunk.content, end="", flush=True)
