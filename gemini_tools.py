from typing import Literal, Any
import asyncio
from json import dumps

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

async def request(
        url: str, 
        method: str,
        *,
        headers: str | dict | None = None,
        json: Any = None,
        data: Any = None,
        cookies: Any = None,
        allow_redirects: bool = True,
        max_redirects: int = 10,
        timeout: int | None = None,
        ) -> dict:
    """
    Perform an asynchronous HTTP request with the specified method and return the response.

    Args:
        url (str): The URL to send the request to.
        method (Literal["GET", "POST", "PUT", "DELETE"]): The HTTP method to use.
        headers (dict, optional): Optional HTTP headers to include in the request.
        json (Any, optional): JSON data to send in the request body.
        data (Any, optional): Raw data to send in the request body.
        cookies (Any, optional): Cookies to include with the request.
        allow_redirects (bool, optional): Whether to follow redirects. Defaults to True.
        max_redirects (int, optional): Maximum number of redirects to follow. Defaults to 10.
        timeout (int, optional): Request timeout in seconds. Defaults to None (no timeout).

    Returns:
        dict: The response from the request. The 'content' key holds the response text and 'status' holds the HTTP status.
    """
    print(f"Making {method} request to URL: {url}")
    if type(headers) == str:
        headers = dumps(headers)

    async with aiohttp.request(method, url, headers=headers, json=json, data=data, cookies=cookies, allow_redirects=allow_redirects, max_redirects=max_redirects, timeout=timeout) as response:
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
    description="Perform an asynchronous HTTP request with the specified method and return the response as a dictionary.",
    parameters=types.Schema(
        type="object",
        properties={
            "url": types.Schema(
                type="string",
                description="The URL to send the request to.",
                example="https://example.com",
            ),
            "method": types.Schema(
                type="string",
                description="The HTTP method to use.",
                enum=["GET", "POST", "PUT", "DELETE"],
            ),
            "headers": types.Schema(
                type="string",
                description="Optional HTTP headers to include in the request.",
                example="{\"User-Agent\": \"Mozilla/5.0\"}",
            ),
            "json": types.Schema(
                type="string",
                description="JSON data to send in the request body.",
                nullable=True,
                example="{\"key\": \"value\"}",
            ),
            "data": types.Schema(
                type="string",
                description="Raw data to send in the request body.",
                nullable=True,
                example="raw data content",
            ),
            "cookies": types.Schema(
                type="string",
                description="Cookies to include with the request.",
                nullable=True,
                example="{\"session_id\": \"abc123\"}",
            ),
            "allow_redirects": types.Schema(
                type="boolean",
                description="Whether to follow redirects. Defaults to True.",
            ),
            "max_redirects": types.Schema(
                type="integer",
                description="Maximum number of redirects to follow. Defaults to 10.",
            ),
            "timeout": types.Schema(
                type="integer",
                description="Request timeout in seconds. Defaults to None (no timeout).",
                nullable=True,
                example=30,
            ),
        },
        required=["url", "method"]
    ),
)

function_declarations = [read_file_tool, write_file_tool, append_file_tool, request_tool]