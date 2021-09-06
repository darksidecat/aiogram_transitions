from typing import Any, Awaitable, Callable, Dict, Type

from aiogram import BaseMiddleware
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Update

from base_machine import MACHINE_STATES, MACHINE_TYPES, BaseMachine

MACHINES = "machines"


class TransitionsMiddleware(BaseMiddleware[Update]):
    machines: Dict[str, Type[BaseMachine]]

    def __init__(self, *machines: Type[BaseMachine]):
        self.machines = dict()
        if machines:
            for machine in machines:
                self.register_machine(machine)

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        fsm_context: FSMContext = data["state"]
        user_data = await fsm_context.get_data()

        machine_type = user_data.get(MACHINE_TYPES)
        machine_state = user_data.get(MACHINE_STATES)

        data[MACHINES] = {}
        if machine_type:
            m = self.machines[machine_type]
            data[MACHINES][machine_type] = m(
                machines=data[MACHINES], initial=machine_state
            )

        result = await handler(event, data)

        user_data = await fsm_context.get_data()
        machine_type: str = user_data.get(MACHINE_TYPES)
        machine: BaseMachine = data[MACHINES].get(machine_type)
        if machine:
            await fsm_context.update_data(
                {
                    MACHINE_TYPES: machine.__class__.__name__,
                    MACHINE_STATES: machine.state,
                }
            )

        return result

    def register_machine(self, machine: Type[BaseMachine]):
        self.machines[machine.__name__] = machine
