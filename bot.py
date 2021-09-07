import asyncio
import logging

import aiogram.types
from aiogram import Bot, Dispatcher
from aiogram.dispatcher.fsm.context import FSMContext

from form import Form
from machines_manager import MachinesManager
from step_machine import StepMachine
from transitions_filter import TransitionsFilter
from transitions_middleware import TransitionsMiddleware

logger = logging.getLogger(__name__)

BOT_TOKEN = "BOT TOKEN"


async def start_form(
    message: aiogram.types.Message,
    state: FSMContext,
    machines_manager: MachinesManager,
):
    form_machine = Form(machines_manager=machines_manager)
    await form_machine.start(state)  # start machine
    await form_machine.proceed(message, state)  # first state

    step_machine = StepMachine(machines_manager=machines_manager)
    await step_machine.start(state)
    await step_machine.proceed(message, state)


async def machine(
    message: aiogram.types.Message,
    machines_manager: MachinesManager,

    state: FSMContext,
):
    form_machine = machines_manager.machine(Form)
    step_machine = machines_manager.machine(StepMachine)
    await step_machine.proceed(message, state)
    await form_machine.proceed(message, state)  # next states


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()

    dp.update.outer_middleware(TransitionsMiddleware(Form, StepMachine))
    dp.message.bind_filter(TransitionsFilter)
    dp.callback_query.bind_filter(TransitionsFilter)

    dp.message.register(start_form, commands={"start"})

    form_states = [
        s for s in Form().states.values() if s.name != "initial"
    ]  # ToDo, improve this
    dp.message.register(machine, t_state=form_states)

    try:
        logger.error("Starting bot")
        await dp.start_polling(bot)
    finally:
        await dp.fsm.storage.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
