from pathlib import Path
from rich.console import Console
import typer
import yaml

from tool.utils.config import LLMConfig, Config
from tool.core.agent_loader import AgentLoader
from tool.cli.chat import chat_command


######## START ########
app = typer.Typer(add_completion=False)
console = Console()
DEFAULT_WORKSPACE = Path(__file__).resolve().parents[2] / "default_workspace"



@app.command()
def main(
    workspace: Path = typer.Option(
        DEFAULT_WORKSPACE, "--workspace", "-w",
        help="Path to workspace directory",
    ),
) -> None:
    """Читает workspace/config.user.yaml и передаёт параметры в run_bot."""
    config_file = workspace.expanduser() / "config.user.yaml"

    if not config_file.exists():
        console.print(f"[yellow]No configuration found at {config_file}[/yellow]")
        raise typer.Exit(1)

    cfg = Config.load(workspace)
    chat_command(cfg, agent_id='default')

if __name__ == "__main__":
    app()