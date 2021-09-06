import logging

from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message

from base_machine import BaseMachine

logger = logging.getLogger(__name__)


class StepMachine(BaseMachine):
    states = ["initial", "stepL", "stepR"]
    transitions = [
        ["proceed", "initial", "stepL"],
        ["proceed", "stepL", "stepR"],
        ["proceed", "stepR", "stepL"],
    ]

    async def on_enter_stepL(self, message: Message, state: FSMContext):
        user_data = await state.get_data()
        step = user_data.get("step")
        if step:
            step += 1
        else:
            step = 1
        await state.update_data(step=step)

        await message.answer("step %sL" % step)

    async def on_enter_stepR(self, message: Message, state: FSMContext):
        user_data = await state.get_data()
        step = user_data.get("step")
        if step:
            step += 1
        else:
            step = 1
        await state.update_data(step=step)

        await message.answer("step %sR" % step)
