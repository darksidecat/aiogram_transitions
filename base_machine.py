from dataclasses import dataclass
from typing import Any, Dict, Optional

from aiogram.dispatcher.fsm.context import FSMContext
from pydantic import BaseModel
from transitions.extensions import AsyncMachine

MACHINE_RECORDS = "machine_types"
MACHINE_STATES = "machine_states"


class MachineRecord(BaseModel):
    type: str
    state: str


MachineRecords = Dict[str, MachineRecord]


class BaseMachine(AsyncMachine):
    states = []
    transitions = []

    def __init__(self, *args, machines: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(
            *args, states=self.states, transitions=self.transitions, **kwargs
        )
        self.machines = machines

    async def start(self, fsm_context: FSMContext):
        if self.machines is not None:
            self.machines[self.__class__.__name__] = self

        user_data = await fsm_context.get_data()
        machine_records: MachineRecords = user_data.get(MACHINE_RECORDS)

        machine_records[self.__class__.__name__] = MachineRecord(
            type=self.__class__.__name__, state=self.state
        )
        await fsm_context.update_data({MACHINE_RECORDS: machine_records})

    async def finish(self, fsm_context: FSMContext):
        if self.machines:
            self.machines.pop(self.__class__.__name__)
        user_data = await fsm_context.get_data()
        machine_records: MachineRecords = user_data.get(MACHINE_RECORDS)

        del machine_records[self.__class__.__name__]

        await fsm_context.update_data({MACHINE_RECORDS: machine_records})
