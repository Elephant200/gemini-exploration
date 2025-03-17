from typing import Literal
import asyncio

import aiofiles
import aiohttp

from google.genai import types

"""
Tools for the Gemini API
"""

async def read_file(file_path: str) -> str:
    """
    Read a file and return the content as a string.

    Args:
        file_path (str): Path to the file.

    Returns:
        str: Content of the file.
    """
    print("Reading file...")
    async with aiofiles.open(file_path, mode="r") as file:
        contents = await file.read()
        return contents

async def write_file(file_path: str, content: str) -> None:
    """
    Write content to a file.

    Args:
        file_path (str): Path to the file.
        content (str): Content to write to the file.
    """
    print("Writing to file...")
    async with aiofiles.open(file_path, mode="w") as file:
        await file.write(content)

async def append_file(file_path: str, content: str) -> None:
    """
    Append content to a file.

    Args:
        file_path (str): Path to the file.
        content (str): Content to append to the file.
    """
    print("Appending to file...")
    async with aiofiles.open(file_path, mode="a") as file:
        await file.write(content)

async def request(url: str, method: str) -> dict:
    """
    Perform an HTTP request with the specified method and return the response text.

    Args:
        url (str): The URL to request.
        method (Literal["GET", "POST", "PUT", "DELETE"]): The HTTP method to use. Defaults to "GET".
        **kwargs: Additional arguments to pass to the request (e.g., headers, json, data).

    Returns:
        dict: The response from the request. The 'content' key holds the response text and 'status' holds the HTTP status.
    """
    print(f"Making {method} request to URL: {url}")
    async with aiohttp.request(method, url) as response:
        response.raise_for_status()
        content = await response.text()
        response_dict = {"content": content, "status": response.status}
        try:
            response_dict["json"] = await response.json()
        except aiohttp.ContentTypeError:
            pass
        return response_dict

all_tools = [read_file, write_file, append_file, request]

read_file_tool = {
    "name": "read_file",
    "description": "Read a file and return the content as a string.",
    "parameters": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the file to read.",
                "example": ""
            }
        }
    }
}

read_file_tool = types.FunctionDeclaration(
    name="read_file",
    description="Read a file and return the content as a string.",
    parameters=types.Schema(
        type="object",
        properties={
            "file_path": types.Schema(
                type="string",
                description="Path to the file to read. This is passed directly into the `aiofiles.open` function; thus, both relative and absolute paths are supported.",
                example="example.txt",
            )
        }
    )
)

write_file_tool = types.FunctionDeclaration(
    name="write_file",
    description="Write content to a file.",
    parameters=types.Schema(
        type="object",
        properties={
            "file_path": types.Schema(
                type="string",
                description="Path to the file to write to. This is passed directly into the `aiofiles.open` function; thus, both relative and absolute paths are supported.",
                example="example.txt",
            ),
            "content": types.Schema(
                type="string",
                description="String content to write to the file.",
                example="Hello, world!",
            )
        }
    )
)

append_file_tool = types.FunctionDeclaration(
    name="append_file",
    description="Append content to a file.",
    parameters=types.Schema(
        type="object",
        properties={
            "file_path": types.Schema(
                type="string",
                description="Path to the file to append to. This is passed directly into the `aiofiles.open` function; thus, both relative and absolute paths are supported.",
                example="example.txt",
            ),
            "content": types.Schema(
                type="string",
                description="String content to append to the file.",
                example="Hello, world!",
            )
        }
    )
)

request_tool = types.FunctionDeclaration(
    name="request",
    description="Perform an HTTP request with the specified method and return the response text.",
    parameters=types.Schema(
        type="object",
        properties={
            "url": types.Schema(
                type="string",
                description="The URL to request.",
                example="https://example.com",
            ),
            "method": types.Schema(
                type="string",
                description="The HTTP method to use. Defaults to 'GET'.",
                example="GET",
                enum=["GET", "POST", "PUT", "DELETE"],
            ),
            "json": types.Schema(
                type="object",
                description="JSON data to send in the request body as \"json\".",
                example={"key": "value"},
            ),
            "data": types.Schema(
                type="object",
                description="Data to send in the request body as \"data\".",
                example={"key": "value"},
            ),
            "headers": types.Schema(
                type="object",
                description="Headers to include in the request.",
                example={"Content-Type": "application/json"},
            ),
            "cookies": types.Schema(
                type="object",
                description="Cookies to include in the request.",
                example={"session": "123"},
            )
        }
    )
)

function_declarations = [read_file_tool, write_file_tool, append_file_tool]