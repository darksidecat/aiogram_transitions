from typing import Any, Dict, Optional

from aiogram.dispatcher.fsm.context import FSMContext
from pydantic import BaseModel
from transitions.extensions import AsyncMachine

MACHINE_RECORDS = "machine_types"
MACHINE_STATES = "machine_states"


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

    def __init__(self, *args, machines: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(
            *args, states=self.states, transitions=self.transitions, **kwargs
        )
        self.machines = machines

    async def start(self, fsm_context: FSMContext):
        if self.machines is not None:
            self.machines[self.__class__.__name__] = self

        user_data = await fsm_context.get_data()
        machine_records: MachineRecords = MachineRecords.parse_raw(
            user_data.get(MACHINE_RECORDS)
        )

        machine_records[self.__class__.__name__] = MachineRecord(
            type=self.__class__.__name__, state=self.state
        )
        await fsm_context.update_data({MACHINE_RECORDS: machine_records.json()})

    async def finish(self, fsm_context: FSMContext):
        if self.machines:
            self.machines.pop(self.__class__.__name__)

        user_data = await fsm_context.get_data()
        machine_records = MachineRecords.parse_raw(user_data.get(MACHINE_RECORDS))
        del machine_records[self.__class__.__name__]

        await fsm_context.update_data({MACHINE_RECORDS: machine_records.json()})
