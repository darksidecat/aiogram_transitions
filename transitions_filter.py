from typing import Dict, List, Optional

from aiogram.dispatcher.filters import BaseFilter
from aiogram.types import TelegramObject

from base_machine import BaseMachine


class TransitionsFilter(BaseFilter):
    machine: BaseMachine
    exclude: Optional[List[str]]

    class Config:
        arbitrary_types_allowed = True

    async def __call__(
        self, obj: TelegramObject, machines: Dict[str, BaseMachine] = None
    ) -> bool:
        if self.machine and machines.get(self.machine.name):
            if self.exclude and machines[self.machine.name].state in self.exclude:
                return False

            return machines[self.machine.name].state in self.machine.states
        return False
