from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict, Type

from aiogram import BaseMiddleware
from aiogram.types import Update

from base_machine import BaseMachine
from machines_manager import MachinesManager

MACHINES = "machines"
MACHINES_MANAGER = "machines_manager"


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

        machine_manager = MachinesManager(registered_machines=self.machines, data=data)
        await machine_manager.create_user_machines()
        data[MACHINES_MANAGER] = machine_manager

        result = await handler(event, data)

        await machine_manager.update_machines_data()
        return result

    def register_machine(self, machine: Type[BaseMachine]):
        self.machines[machine.__name__] = machine
