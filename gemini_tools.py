import aiofiles

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
