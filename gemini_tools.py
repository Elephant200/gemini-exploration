from typing import Literal
import aiofiles
import aiohttp

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

async def request(url: str, method: Literal["GET", "POST", "PUT", "DELETE"] = "GET", **kwargs) -> str:
    """
    Perform an HTTP request with the specified method and return the response text.

    Args:
        url (str): The URL to request.
        method (Literal["GET", "POST", "PUT", "DELETE"]): The HTTP method to use. Defaults to "GET".
        **kwargs: Additional arguments to pass to the request (e.g., headers, json, data).

    Returns:
        str: The response text from the request.
    """
    print(f"Making {method} request to URL: {url}")
    async with aiohttp.request(method, url, **kwargs) as response:
        response.raise_for_status()
        return await response.text()