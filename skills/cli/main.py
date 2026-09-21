from pathlib import Path
from rich.console import Console
import typer
import yaml

from skills.cli.chat import chat_command
from skills.core.skill_loader import SkillDef
from skills.utils.config import Config


######## START ########
app = typer.Typer(add_completion=False)
console = Console()
DEFAULT_WORKSPACE = Path(__file__).resolve().parents[2] / "default_workspace"


def parse_skill_def(
    def_id: str, frontmatter: dict, body: str):
    try:
        return SkillDef(
            id=def_id,
            name=frontmatter["name"],  # type: ignore[misc]
            description=frontmatter["description"],  # type: ignore[misc]
            content=body.strip(),
        )
    except Exception as e:
        print(f"Invalid skill '{def_id}': {e}")
        return None
    except KeyError as e:
        print(f"Missing required field in skill '{def_id}': {e}")
        return None



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