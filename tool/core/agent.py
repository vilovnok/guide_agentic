import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

from tool.provider.llm import LLMProvider
from tool.core.session_state import SessionState
from tool.tools.tools import read_file, write_file, edit_file, bash

from langchain_core.messages import ToolMessage

if TYPE_CHECKING:
    from tool.core.agent_loader import AgentDef
    from tool.utils.config import Config




MAX_STEPS = 10

class Agent:
    def __init__(self, agent_def: "AgentDef", config: "Config") -> None:
        self.agent_def = agent_def
        self.config = config
        self.llm = LLMProvider.from_config(agent_def.llm)

        self.tools = [read_file, write_file, edit_file, bash]
        self.tools_by_name = {t.name: t for t in self.tools}

    def new_session(self, session_id: str | None = None) -> "AgentSession":
        session_id = session_id or str(uuid.uuid4())

        state = SessionState(
            session_id=session_id,
            agent=self,
            messages=[],
        )

        session = AgentSession(agent=self, state=state)
        return session


@dataclass
class AgentSession:
    """Chat orchestrator - operates on swappable SessionState."""

    agent: Agent
    state: SessionState
    started_at: datetime = field(default_factory=datetime.now)

    @property
    def session_id(self) -> str:
        """Delegate to state."""
        return self.state.session_id

    async def _run_tool(self, call: dict) -> str:
        tool = self.agent.tools_by_name.get(call["name"])
        if tool is None:
            return f"Error: unknown tool '{call['name']}'"
        try:
            return str(await tool.ainvoke(call["args"]))
        except Exception as e:
            return f"Error: {e}"


    # async def chat(self, message: str) -> str:
    #     """Send a message to the LLM and get a response."""
    #     user_msg: Message = {"role": "user", "content": message}
    #     self.state.add_message(user_msg)

    #     messages = self.state.build_message()
    #     response = await self.agent.llm.chat(messages)
    #     assistant_msg: Message = {"role": "assistant", "content": response}
    #     self.state.add_message(assistant_msg)

    #     return response


    async def chat(self, message: str) -> str:
        self.state.add_message({"role": "user", "content": message})
        messages = self.state.build_message() 

        for _ in range(MAX_STEPS):
            ai = await self.agent.llm.complete(messages, tools=self.agent.tools)
            messages.append(ai)

            if not ai.tool_calls:              
                break

            for call in ai.tool_calls:         
                result = await self._run_tool(call)
                messages.append(
                    ToolMessage(content=result, tool_call_id=call["id"], name=call["name"])
                )
        else:
            return "Error: tool call limit reached"

        answer = self.agent.llm.text_of(ai)
        self.state.add_message({"role": "assistant", "content": answer})
        return answer