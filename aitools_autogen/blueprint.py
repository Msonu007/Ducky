from typing import Optional

from autogen import ConversableAgent


class Blueprint:

    def __init__(self,
                 agents: Optional[list[ConversableAgent]] = None,
                 config_list: Optional[list[dict]] = None,
                 llm_config: Optional[dict] = None):
        self._agents = agents or None
        self._config_list = config_list or None
        self._llm_config = llm_config or None

        self._initiator = agents[0] if agents else None
        self._recipient = agents[1] if agents and len(agents) > 1 else None

    async def initiate_work(self, message: str):
        if self._initiator and self._recipient:
            self._initiator.initiate_chat(recipient=self._recipient, message=message)
        else:
            raise ValueError("No initiator or recipient agent found.")
