import os
import logging
from dotenv import load_dotenv
from google import genai
from google.genai import types
import asyncio

load_dotenv()

logging.basicConfig()
logger = logging.getLogger(__name__)

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"), http_options={'api_version': 'v1alpha'})

def read_file(filename: str) -> str:
    """
    Returns the file content of the given file
    """
    print("YAY!! GEMINI IS SMART!!")
    try:
        with open(filename, "r") as f:
            content = f.read()
    except Exception as e:
        logging.error(f"File could not be read: {e}")
        return None
    return content

search_tool = {"google_search": {}}

config = {"generation_config": {"response_modalities": ["TEXT"]}}


async def main(config, model: str = "gemini-2.0-flash-exp"):
    async with client.aio.live.connect(model=model, config=config) as session:
        logger.debug("Session created")
        print("Welcome to Gemini ChatBot! Type 'quit' to exit.")
        while True:
            query = input("User   > ")
            if query.lower() == "quit":
                print("Exiting the chat. Goodbye!")
                break
            await session.send(input=query, end_of_turn=True)
            print("Gemini > ", end="")
            async for response in session.receive():
                if response.text is None:
                    logger.debug("Received non-text response; ignored.")
                    continue
                print(response.text, end="")

asyncio.run(main(config=config))