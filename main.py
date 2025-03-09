import os
import logging
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError
import asyncio

# USE THIS LINK FOR REFERENCE:
# https://github.com/google-gemini/cookbook/blob/main/quickstarts/Get_started_LiveAPI.py

load_dotenv()

logging.basicConfig(level="WARNING")
logger = logging.getLogger(__name__)

search_tool = {"google_search": {}}

async def read_file(file_path: str) -> str:
    """
    Read a file and return the content as a string.

    Args:
        file_path (str): Path to the file.

    Returns:
        str: Content of the file.
    """
    print("Reading file...")
    return "This is the content of the file."

def handle_server_content(server_content):
    model_turn = server_content.model_turn
    if model_turn:
        for part in model_turn.parts:
            executable_code = part.executable_code
            if executable_code is not None:
                print('-------------------------------')
                print(f'``` python\n{executable_code}\n```')
                print('-------------------------------')

            code_execution_result = part.code_execution_result
            if code_execution_result is not None:
                print('-------------------------------')
                print(f'```\n{code_execution_result}\n```')
                print('-------------------------------')

    grounding_metadata = getattr(server_content, 'grounding_metadata', None)
    if grounding_metadata is not None:
        print(grounding_metadata.search_entry_point.rendered_content)


async def handle_tool_call(session, tool_call):
    """
    Handle tool call and send the response back to the chatbot.

    Args:

    """
    print(type(session))
    print(type(tool_call))
    responses = []
    for function_call in tool_call.function_calls:
        print(function_call)
        responses.append(types.FunctionResponse(
            name=function_call.name,
            id=function_call.id,
            response={'result':'ok'},
        ))
    
    tool_response = types.LiveClientToolResponse(
        function_responses=responses,
    )

    print('\n>>> ', tool_response)
    await session.send(input=tool_response)

async def send_text(session):
    while True:
        text = await asyncio.to_thread(
            input,
            "message > ",
        )
        if text.lower() == "q":
            break
        await session.send(input=text or ".", end_of_turn=True)

async def main(config: dict, model: str = "gemini-2.0-flash-exp", typing_speed: str = "MEDIUM"):
    """
    Main function to run the chatbot.

    Args:
        config (dict): Configuration for the chatbot.
        model (str): Gemini model name to use for the chatbot. Defaults to "gemini-2.0-flash-exp."
        typing_speed (str): Typing speed for the chatbot. Can be 
            "VERY_FAST", "FAST", "MEDIUM", "SLOW", "VERY_SLOW", or "INSTANT".
            If "INSTANT" is selected, the chat message will show parts as soon as they are received.
            Defaults to "MEDIUM".
    """

    typing_delay = {"VERY_FAST": 0.005, "FAST": 0.01, "MEDIUM": 0.015, "SLOW": 0.02, "VERY_SLOW": 0.03, "INSTANT": 0}.get(typing_speed, None)
    if typing_delay is None:
        raise ValueError("Invalid typing speed. Please select from 'VERY_FAST', 'FAST', 'MEDIUM', 'SLOW', 'VERY_SLOW', or 'INSTANT'.") 

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"), http_options={'api_version': 'v1alpha'})
    logger.debug("Client created")

    try:
        async with client.aio.live.connect(model=model, config=config) as session:
            print(type(session))
            logger.debug("Chat session created")
            print("Welcome to Gemini ChatBot! Type 'quit' to exit.")
            while True:
                query = input("User   > ")
                if query.lower() == "quit":
                    print("Exiting the chat. Goodbye!")
                    break
                await session.send(input=query, end_of_turn=True)
                print("Gemini > ", end="")
                async for response in session.receive():

                    if response.text:
                        print(response.text, end="", flush=True)
                        continue
                    
                    if response.server_content is not None:
                        handle_server_content(response.server_content)
                        continue

                    if response.tool_call is not None:
                        await handle_tool_call(session, response.tool_call)
                        continue

                    if response.tool_call:
                        print(response.tool_call, end="", flush=True)
                        continue
                    
                    # for word in response.text.split(" "):
                    #     print(word, end=" ", flush=True)
                    #     await asyncio.sleep(typing_delay*4)
    
    except APIError as e:
        logger.error(e)
        print(f"There was an API Error. Please check the logs for more information.")
    except Exception as e:
        logger.error(e)
        print(f"An error occured. Please try again later.")


tools = [search_tool]

config = types.LiveConnectConfig(
    system_instruction=types.Content(
        parts=[
            types.Part(
                text="You are a helpful assistant running on the Google Gemini 2.0 Flash Exp model. You are running on VSCode through the Multimodal Live API. Answer prompts concisely unless otherwise stated."
            )
        ]
    ),
    tools=tools,
    response_modalities=["TEXT"]
)

asyncio.run(main(config=config, typing_speed="MEDIUM"))