"""Agent на базе langchain.agents.create_agent.

create_agent = цикл LLM -> tool_calls -> ToolNode (параллельно) -> LLM,
история диалога хранится в checkpointer по thread_id.
Поэтому не нужны: LLMProvider, ToolRegistry, SessionState, ручной while-цикл.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from skills.core.skill_loader import SkillLoader
from skills.tools import build_builtin_tools, create_skill_tool
from skills.utils.llm import build_chat_model

if TYPE_CHECKING:
    from skills.core.agent_loader import AgentDef
    from skills.utils.config import Config


class Agent:
    """Настроенный агент; создаёт сессии (thread'ы)."""

    def __init__(self, agent_def: "AgentDef", config: "Config") -> None:
        self.agent_def = agent_def
        self.config = config
        self.skill_loader = SkillLoader(config)

        tools = build_builtin_tools(config.workspace)
        if agent_def.allow_skills:
            skill_tool = create_skill_tool(self.skill_loader)
            if skill_tool:
                tools.append(skill_tool)

        self.checkpointer = InMemorySaver()
        self.graph = create_agent(
            model=build_chat_model(agent_def.llm),
            tools=tools,
            system_prompt=agent_def.agent_md,
            checkpointer=self.checkpointer,
        )

    def new_session(self, session_id: str | None = None) -> "AgentSession":
        return AgentSession(agent=self, session_id=session_id or str(uuid.uuid4()))


@dataclass
class AgentSession:
    agent: Agent
    session_id: str
    started_at: datetime = field(default_factory=datetime.now)

    async def chat(self, message: str) -> str:
        result = await self.agent.graph.ainvoke(
            {"messages": [{"role": "user", "content": message}]},
            config={"configurable": {"thread_id": self.session_id}},
        )
        return result["messages"][-1].text
