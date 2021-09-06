from __future__ import annotations

from typing import TYPE_CHECKING, Dict

from aiogram.dispatcher.fsm.context import FSMContext
from pydantic import BaseModel
from transitions.extensions import AsyncMachine

if TYPE_CHECKING:
    from machines_manager import MachinesManager


class MachineRecord(BaseModel):
    type: str
    state: str


class MachineRecords(BaseModel):
    __root__: Dict[str, MachineRecord]

    def __setitem__(self, key, value):
        self.__root__[key] = value

    def __getitem__(self, item):
        return self.__root__[item]

    def __delitem__(self, key):
        del self.__root__[key]

    def values(self):
        return self.__root__.values()


class BaseMachine(AsyncMachine):
    states = []
    transitions = []

    def __init__(self, *args, machines_manager: MachinesManager, **kwargs):
        super().__init__(
            *args, states=self.states, transitions=self.transitions, **kwargs
        )
        self.name = self.__class__.__name__
        self.machines_manager = machines_manager

    async def start(self, fsm_context: FSMContext):
        await self.machines_manager.activate_machine(self)

    async def finish(self, fsm_context: FSMContext):
        await self.machines_manager.deactivate_machine(self)
