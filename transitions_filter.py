from typing import List, Union

from aiogram.dispatcher.filters import BaseFilter
from aiogram.types import TelegramObject
from pydantic import validator
from transitions.extensions.asyncio import AsyncMachine, AsyncState


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

    async def __call__(self, obj: TelegramObject, machine: AsyncMachine) -> bool:
        if self.t_state and machine and machine.state:
            return machine.state in [s.name for s in self.t_state]
        return False
