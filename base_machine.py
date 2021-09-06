from typing import Any, Dict, Optional

from aiogram.dispatcher.fsm.context import FSMContext
from transitions.extensions import AsyncMachine

MACHINE_TYPES = "machine_types"
MACHINE_STATES = "machine_states"


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
        await fsm_context.update_data(
            {MACHINE_TYPES: self.__class__.__name__, MACHINE_STATES: self.state}
        )

    async def finish(self, fsm_context: FSMContext):
        if self.machines:
            self.machines.pop(self.__class__.__name__)
        await fsm_context.update_data(
            {
                MACHINE_TYPES: None,
                MACHINE_STATES: None,
            }
        )
