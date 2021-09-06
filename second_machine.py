import logging

from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message

from base_machine import BaseMachine

logger = logging.getLogger(__name__)


class StepMachine(BaseMachine):
    states = ["initial", "step"]
    transitions = [
        ["proceed", "initial", "step"],
        ["proceed", "step", "step"],
    ]

    async def on_enter_step(self, message: Message, state: FSMContext):
        user_data = await state.get_data()
        step = user_data.get("step")
        if step:
            step += 1
        else:
            step = 1
        await state.update_data(step=step)

        await message.answer("step %s" % step)
