"""Skill loader for discovering and loading skills."""

import logging
from typing import Any

from pydantic import BaseModel, ConfigDict, ValidationError

from skills.utils.config import Config
from skills.utils.def_loader import DefNotFoundError, discover_definitions

logger = logging.getLogger(__name__)


class SkillDef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    description: str
    content: str


def _parse_skill(def_id: str, meta: dict[str, Any], body: str) -> SkillDef | None:
    try:
        return SkillDef(
            id=def_id,
            name=meta["name"],
            description=meta["description"],
            content=body.strip(),
        )
    except (KeyError, ValidationError) as e:
        logger.warning("Invalid skill '%s': %s", def_id, e)
        return None


class SkillLoader:
    def __init__(self, config: Config):
        self.config = config

    def discover_skills(self) -> list[SkillDef]:
        return discover_definitions(self.config.skills_path, "SKILL.md", _parse_skill)

    def load_skill(self, skill_id: str) -> SkillDef:
        for skill in self.discover_skills():
            if skill.id == skill_id:
                return skill
        raise DefNotFoundError("skill", skill_id)