import json
from typing import Any, Awaitable, Callable, Dict, Type

from aiogram import BaseMiddleware
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Update

from base_machine import MACHINE_RECORDS, BaseMachine, MachineRecord, MachineRecords

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

        data[MACHINES] = {}
        records = user_data.get(MACHINE_RECORDS)
        if records:
            machine_records: MachineRecords = MachineRecords.parse_raw(records)

            for machine_record in machine_records.values():
                m = self.machines[machine_record.type]
                data[MACHINES][machine_record.type] = m(
                    machines=data[MACHINES],
                    initial=machine_records[machine_record.type].state,
                )
        else:
            await fsm_context.update_data(
                {MACHINE_RECORDS: MachineRecords.parse_obj({}).json()}
            )

        result = await handler(event, data)

        user_data = await fsm_context.get_data()
        records = user_data.get(MACHINE_RECORDS)
        if records:
            machine_records: MachineRecords = MachineRecords.parse_raw(records)

            for machine_record in machine_records.values():
                machine: BaseMachine = data[MACHINES].get(machine_record.type)
                if machine:
                    machine_records[machine_record.type] = MachineRecord(
                        type=machine.__class__.__name__, state=machine.state
                    )

                    await fsm_context.update_data(
                        {MACHINE_RECORDS: machine_records.json()}
                    )

        return result

    def register_machine(self, machine: Type[BaseMachine]):
        self.machines[machine.__name__] = machine
