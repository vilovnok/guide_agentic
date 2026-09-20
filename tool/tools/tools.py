import asyncio
from pathlib import Path

from langchain.tools import tool




@tool('read', parse_docstring=True)
def read_file(path: str) -> str:
    """
    Read the contents of a text file.
    
    Args:
        path (str): The path to the file to read.
    """
    try:
        return Path(path).read_text()
    except FileNotFoundError:
        return f"Error: File not found: {path}"
    except PermissionError:
        return f"Error: Permission denied reading: {path}"
    except IsADirectoryError:
        return f"Error: Path is a directory, not a file: {path}"
    except Exception as e:
        return f"Error reading file: {e}"


@tool('write', parse_docstring=True)
async def write_file(path: str, content: str) -> str:
    """
    Write content to a file at the given path.

    Args:
        path (str): The path to the file to write.
        content (str): The content to write to the file.
    """
    try:
        Path(path).write_text(content)
        return f"Successfully wrote to: {path}"
    except PermissionError:
        return f"Error: Permission denied writing to: {path}"
    except IsADirectoryError:
        return f"Error: Path is a directory, not a file: {path}"
    except Exception as e:
        return f"Error writing file: {e}"


@tool('edit', parse_docstring=True)
async def edit_file(
    path: str, old_text: str, new_text: str) -> str:
    """
    Edit a file by replacing old_text with new_text.

    Args:
        path (str): The path to the file to edit.
        old_text (str): The text to be replaced.
        new_text (str): The text to replace old_text with.
    """
    try:
        content = Path(path).read_text()
        if old_text not in content:
            return f"Error: '{old_text}' not found in {path}"
        new_content = content.replace(old_text, new_text)
        Path(path).write_text(new_content)
        return f"Successfully edited {path}"
    except FileNotFoundError:
        return f"Error: File not found: {path}"
    except PermissionError:
        return f"Error: Permission denied editing: {path}"
    except Exception as e:
        return f"Error editing file: {e}"


@tool('bash', parse_docstring=True)
async def bash(command: str) -> str:
    """
    Execute a bash shell command.

    Args:
        command (str): The bash command to execute.
    """
    try:
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        output = stdout.decode() if stdout else ""
        error = stderr.decode() if stderr else ""
        if output and error:
            return f"{output}\n{error}"
        return output or error or "Command completed with no output"
    except Exception as e:
        return f"Error executing command: {e}"