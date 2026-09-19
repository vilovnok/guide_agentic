from dataclasses import dataclass
from typing import TYPE_CHECKING

from chat_loop.provider.llm import Message



if TYPE_CHECKING:
    from chat_loop.core.agent import Agent



@dataclass
class SessionState:

    session_id: str
    agent: "Agent"
    messages: list[Message]

    def add_message(self, message: Message) -> None:
        self.messages.append(message)

    def build_message(self) -> list[Message]:
        system_prompt = self.agent.agent_def.agent_md
        messages: list[Message] = [{"role": "system", "content": system_prompt}]
        messages.extend(self.messages)
        return messages