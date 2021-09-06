from __future__ import annotations

from typing import Any, Dict, Type

from base_machine import BaseMachine, MachineRecord, MachineRecords

MACHINES = "machines"
MACHINE_RECORDS = "machine_types"


class MachinesManager:
    def __init__(
        self, registered_machines: Dict[str, Type[BaseMachine]], data: Dict[str, Any]
    ):
        self.fsm_context = data["state"]
        self.active_machines = data.setdefault(MACHINES, {})
        self.registered_machines = registered_machines

    async def activate_machine(self, machine: BaseMachine):
        self.active_machines[machine.name] = machine

        user_data = await self.fsm_context.get_data()
        machine_records: MachineRecords = MachineRecords.parse_raw(
            user_data.get(MACHINE_RECORDS)
        )

        machine_records[machine.name] = MachineRecord(
            type=machine.name, state=machine.state
        )
        await self.fsm_context.update_data({MACHINE_RECORDS: machine_records.json()})

    async def deactivate_machine(self, machine):
        if self.active_machines:
            self.active_machines.pop(machine.name)

        user_data = await self.fsm_context.get_data()
        machine_records = MachineRecords.parse_raw(user_data.get(MACHINE_RECORDS))
        del machine_records[machine.name]

        await self.fsm_context.update_data({MACHINE_RECORDS: machine_records.json()})

    def manager(self, manager: Type[BaseMachine]):
        return self.active_machines.get(manager.__name__)

    async def create_user_machines(self):
        user_data = await self.fsm_context.get_data()

        records = user_data.get(MACHINE_RECORDS)
        if records:
            machine_records: MachineRecords = MachineRecords.parse_raw(records)

            for machine_record in machine_records.values():
                m = self.registered_machines[machine_record.type]
                self.active_machines[machine_record.type] = m(
                    machines_manager=self,
                    initial=machine_records[machine_record.type].state,
                )
        else:
            await self.fsm_context.update_data(
                {MACHINE_RECORDS: MachineRecords.parse_obj({}).json()}
            )

    async def update_machines_data(self):
        user_data = await self.fsm_context.get_data()
        records = user_data.get(MACHINE_RECORDS)
        if records:
            machine_records: MachineRecords = MachineRecords.parse_raw(records)

            for machine_record in machine_records.values():
                machine: BaseMachine = self.active_machines.get(machine_record.type)
                if machine:
                    machine_records[machine_record.type] = MachineRecord(
                        type=machine.name, state=machine.state
                    )

                    await self.fsm_context.update_data(
                        {MACHINE_RECORDS: machine_records.json()}
                    )
