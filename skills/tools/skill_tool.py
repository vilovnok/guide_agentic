"""skill-tool как LangChain StructuredTool с динамической схемой."""

from typing import TYPE_CHECKING, Literal

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from skills.core.skill_loader import SkillLoader


def create_skill_tool(skill_loader: "SkillLoader") -> StructuredTool | None:
    skills = skill_loader.discover_skills()
    if not skills:
        return None

    skills_xml = "<skills>\n" + "\n".join(
        f'  <skill name="{s.name}">{s.description}</skill>' for s in skills
    ) + "\n</skills>"

    SkillId = Literal[tuple(s.id for s in skills)] 

    class SkillInput(BaseModel):
        skill_name: SkillId = Field(description="The name of the skill to load") 

    def load_skill(skill_name: str) -> str:
        try:
            return skill_loader.load_skill(skill_name).content
        except Exception:
            return f"Error: Skill '{skill_name}' not found. It may have been removed or is unavailable."

    return StructuredTool.from_function(
        func=load_skill,
        name="skill",
        description=f"Load and invoke a specialized skill. {skills_xml}",
        args_schema=SkillInput,
    )
