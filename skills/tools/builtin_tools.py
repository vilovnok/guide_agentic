"""Встроенные инструменты: файловые — готовый FileManagementToolkit, edit/bash — свои через @tool."""

import asyncio
from pathlib import Path

from langchain_community.agent_toolkits import FileManagementToolkit
from langchain_core.tools import BaseTool, tool


def make_edit_tool(root: Path) -> BaseTool:
    """В LangChain нет готового edit-тула — оставляем свой, но через @tool."""
    root = root.resolve()

    @tool
    def edit(path: str, old_text: str, new_text: str) -> str:
        """Edit a file by replacing old_text with new_text (exact match)."""
        target = (root / path).resolve()
        if not target.is_relative_to(root):
            return f"Error: path is outside the workspace: {path}"
        try:
            content = target.read_text()
        except FileNotFoundError:
            return f"Error: File not found: {path}"
        if old_text not in content:
            return f"Error: '{old_text}' not found in {path}"
        target.write_text(content.replace(old_text, new_text))
        return f"Successfully edited {path}"

    return edit


@tool
async def bash(command: str) -> str:
    """Execute a bash shell command and return its output."""
    proc = await asyncio.create_subprocess_shell(
        command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    out, err = await proc.communicate()
    text = "\n".join(x.decode() for x in (out, err) if x)
    return text or "Command completed with no output"


def build_builtin_tools(workspace: Path) -> list[BaseTool]:
    """read_file / write_file / list_directory (с песочницей root_dir) + edit + bash."""
    fs_tools = FileManagementToolkit(
        root_dir=str(workspace),
        selected_tools=["read_file", "write_file", "list_directory"],
    ).get_tools()
    return [*fs_tools, make_edit_tool(workspace), bash]
