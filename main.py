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

class GeminiChat:
    def __init__(self, api_key: str | None = None, config: types.LiveConnectConfigOrDict | None = None, tools: types.ToolListUnion | None = None, system_instruction: str | types.Content | None = None, model: str = "gemini-2.0-flash-exp"):
        """
        Initialize the GeminiChat class, which uses the Multimodal Live API with Google's gemini-2.0-flash-exp model.

        Args:
            api_key (str, optional): API key for the Gemini API. Defaults to None.
            config (types.LiveConnectConfigOrDict, optional): Configuration for the chatbot. Defaults to None.
            tools (ToolListUnion, optional): List of tools to use for the chatbot. Defaults to including the Gemini API.
            model (str, optional): Gemini model name to use for the chatbot. Defaults to "gemini-2.0-flash-exp".
            system_instruction (str, optional): System instruction for the chatbot. Defaults to None.
        """
        self.client = genai.Client(api_key=api_key or os.getenv("GEMINI_API_KEY"), http_options={'api_version': 'v1alpha'})
        self.model = model

        if config:
            self.config = (types.LiveConnectConfig)(config)
            if config.response_modalities != [types.Modality.TEXT]:
                logger.warning("Response modalities other than TEXT are not supported.")
                config.response_modalities = [types.Modality.TEXT]
            if config.response_modalities is None:
                config.response_modalities = [types.Modality.TEXT]
        else:
            self.config = types.LiveConnectConfig(
                response_modalities=[types.Modality.TEXT],
            )

        if self.config.system_instruction is not None and system_instruction is not None:
            logger.warning("Overwriting system_instruction in the config.")

        if system_instruction:
            if type(system_instruction) == str:
                self.config.system_instruction = types.Content(parts=[types.Part(text=system_instruction)])
            elif type(system_instruction) == types.Content:
                self.config.system_instruction = system_instruction
            else:
                raise ValueError("Invalid system_instruction type. Please provide a string or a Content object.")
        
        if self.config.tools is not None and tools is not None:
            logger.warning("Overwriting tools in the config.")

        if tools:
            self.config.tools = tools
        
        self.session = None

    async def handle_server_content(self, server_content):
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
            logger.info(grounding_metadata.search_entry_point.rendered_content)

    async def handle_tool_call(self, tool_call):
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

        logger.info('\nTool Response: ', tool_response)
        await self.session.send(input=tool_response)

    async def run(self):
        try:
            async with self.client.aio.live.connect(model=self.model, config=self.config) as session:
                print("Welcome to Gemini ChatBot! Type 'quit' to exit.")

                while True:

                    query = input("User   > ")
                    if query.lower() == "quit":
                        raise KeyboardInterrupt("User exited the chat.")
                    
                    elif query.strip() == "":
                        continue # Prevent sending empty queries

                    await session.send(input=query, end_of_turn=True)
                    print("Gemini > ", end="")
                    async for response in session.receive():
                        logger.info(type(response))
                        if response.text:
                            print(response.text, end="")
                            continue
                        
                        if response.server_content:
                            await self.handle_server_content(response.server_content)
                            continue

                        if response.tool_call:
                            await self.handle_tool_call(response.tool_call)
                            continue

        
        except KeyboardInterrupt as e:
            print("System > Exiting the chat. Goodbye!")

        except Exception as e:
            logger.error(e)
            print(type(e))
            print(f"System > An error occured. Please try again later.")


function_declarations = [read_file]



tools = [
    {"google_search": {}}
    ]

system_instruction = """
You are a helpful assistant running on the Google Gemini 2.0 Flash Exp model. 

You are running on VSCode through the Multimodal Live API."
"""

chat = GeminiChat(system_instruction=system_instruction, tools=tools)
asyncio.run(chat.run())