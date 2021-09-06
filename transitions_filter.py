from typing import Dict, List, Optional, Union

from aiogram.dispatcher.filters import BaseFilter
from aiogram.types import TelegramObject
from pydantic import validator
from transitions.extensions.asyncio import AsyncState

from base_machine import BaseMachine


class TransitionsFilter(BaseFilter):
    t_state: Union[List[AsyncState], AsyncState]

    class Config:
        arbitrary_types_allowed = True

    @validator("t_state")
    def _validate_t_state(
        cls, value: Union[List[AsyncState], AsyncState]
    ) -> List[AsyncState]:
        if isinstance(value, AsyncState):
            value = [value]
        return value

    async def __call__(
        self, obj: TelegramObject, machines: Optional[Dict[str, BaseMachine]] = None
    ) -> bool:
        if self.t_state and machines:
            t_states = [s.name for s in self.t_state]
            return any([machine.state in t_states for machine in machines.values()])
        return False
