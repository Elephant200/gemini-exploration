import os
import logging
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError
import asyncio

from websockets import ConnectionClosedError

# USE THIS LINK FOR REFERENCE:
# https://github.com/google-gemini/cookbook/blob/main/quickstarts/Get_started_LiveAPI.py
# 

load_dotenv()

logging.basicConfig(level="INFO")
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
    # Currently a placeholder response
    return "This is the content of the file."

class GeminiChat:
    def __init__(self, api_key: str | None = None, config: types.LiveConnectConfig | None = None, model: str = "gemini-2.0-flash-exp"):
        """
        Initialize the GeminiChat class, which uses the Multimodal Live API with Google's gemini-2.0-flash-exp model.

        Args:
            api_key (str, optional): API key for the Gemini API. Defaults to None.
            config (types.LiveConnectConfigOrDict, optional): Configuration for the chatbot. Defaults to None. Include system instructions and tools here.
            model (str, optional): Gemini model name to use for the chatbot. Defaults to "gemini-2.0-flash-exp".
        """
        self.client = genai.Client(api_key=api_key or os.getenv("GOOGLE_API_KEY"), http_options={'api_version': 'v1alpha'})
        self.model = model

        if config:
            self.config = config
            if config.response_modalities != [types.Modality.TEXT]:
                logger.warning("Response modalities other than TEXT are not supported.")
                config.response_modalities = [types.Modality.TEXT]
            if config.response_modalities is None:
                config.response_modalities = [types.Modality.TEXT]
        else:
            self.config = types.LiveConnectConfig(
                response_modalities=[types.Modality.TEXT],
                system_instruction=types.Content(parts=[types.Part(text="You are a helpful assistant running on the Google Gemini 2.0 Flash Exp model. You are running through the Multimodal Live API. Answer prompts concisely.")]),
                tools=[types.Tool(google_search=types.GoogleSearch())],
            )
        
        self.session = None

        self.history = [
            types.Content(parts=[types.Part(text=system_instruction)], role="system")
        ]

    async def handle_server_content(self, server_content):
        model_turn = server_content.model_turn
        if model_turn:
            for part in model_turn.parts:
                executable_code = part.executable_code
                if executable_code is not None:
                    print('--------Executable Code--------')
                    print(f'``` python\n{executable_code}\n```')
                    print('-------------------------------')

                code_execution_result = part.code_execution_result
                if code_execution_result is not None:
                    print('-----Code Execution Result-----')
                    print(f'```\n{code_execution_result}\n```')
                    print('-------------------------------')

        grounding_metadata = getattr(server_content, 'grounding_metadata', None)
        if grounding_metadata is not None:
            logger.info(grounding_metadata.search_entry_point.rendered_content)

    async def handle_tool_call(self, tool_call):
        print('--------Handle Tool Call-------')
        responses = []
        for function_call in tool_call.function_calls:
            print("Function Call: " + str(function_call))
            responses.append(types.FunctionResponse(
                name=function_call.name,
                id=function_call.id,
                response={"output": "Elephants rule!!"}, # Currently a placeholder response
            ))
        
        tool_response = types.LiveClientToolResponse(
            function_responses=responses,
        )

        print('Tool Response: ' + str(tool_response))
        print('-------------------------------')


        await self.session.send(input=tool_response)

    async def run(self):
        try:
            async with self.client.aio.live.connect(model=self.model, config=self.config) as session:
                self.session = session

                print("Welcome to Gemini ChatBot! Type 'quit' to exit.")

                while True:

                    query = input("User   > ")
                    if query.lower() == "quit":
                        raise KeyboardInterrupt("User exited the chat.")
                    
                    elif query.strip() == "":
                        continue # Prevent sending empty queries
                    
                    self.history.append(types.Content(parts=[types.Part(text=query)], role="user"))
    
                    await self.session.send(input=query, end_of_turn=True)

                    print("Gemini > ", end="")
                    full_response = []
                    
                    async for response in self.session.receive(): # type(response) = types.LiveServerMessage
                        try:
                            if response.server_content.model_turn is not None:
                                    
                                full_response.append(response.server_content.model_turn.parts[0])
                        except:
                            print(response)

                        if response.text:
                            print(response.text, end="")
                            continue

                        if response.server_content:
                            await self.handle_server_content(response.server_content)
                            continue

                        if response.tool_call:
                            await self.handle_tool_call(response.tool_call)
                            continue

                    self.history.append(types.Content(parts=full_response, role="model"))

        except asyncio.CancelledError as e:
            print("\nSystem > The chat has been cancelled. Goodbye!")

        except KeyboardInterrupt as e:
            print("System > Exiting the chat. Goodbye!")

        except ConnectionClosedError as e:
            print("\nSystem > The session timed out.")

        except Exception as e:
            logger.error(e)
            logger.error(type(e))
            print(f"System > An error occured. Please try again later.")
        
        print("System > " + str(self.history))

tools = [
    {"google_search": {}},
    read_file
    ]

system_instruction = """
You are a helpful assistant running on the Google Gemini 2.0 Flash Exp model. 

You are running on VSCode through the Multimodal Live API."
"""

config = types.LiveConnectConfig(
    tools=tools
)

chat = GeminiChat(config=config)
asyncio.run(chat.run())