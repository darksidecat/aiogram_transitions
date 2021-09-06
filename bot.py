import asyncio
import logging
from typing import Dict

import aiogram.types
from aiogram import Bot, Dispatcher
from aiogram.dispatcher.fsm.context import FSMContext

from base_machine import BaseMachine
from form import Form
from transitions_filter import TransitionsFilter
from transitions_middleware import TransitionsMiddleware

logger = logging.getLogger(__name__)

BOT_TOKEN = "BOT TOKEN"


async def start_form(
    message: aiogram.types.Message,
    state: FSMContext,
    machines: Dict[str, BaseMachine],
):
    form_machine = Form(machines=machines)
    await form_machine.start(state)  # start machine
    await form_machine.proceed(message, state)  # first state


async def machine(
    message: aiogram.types.Message,
    machines: Dict[str, BaseMachine],
    state: FSMContext,
):
    form_machine = machines.get(Form.__name__)
    await form_machine.proceed(message, state)  # next states


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()

    dp.update.outer_middleware(TransitionsMiddleware(Form))
    dp.message.bind_filter(TransitionsFilter)
    dp.callback_query.bind_filter(TransitionsFilter)

    dp.message.register(start_form, commands={"start"})

    form_states = [s for s in Form().states.values()]  # ToDo, improve this
    dp.message.register(machine, t_state=form_states)

    try:
        logger.error("Starting bot")
        await dp.start_polling(bot)
    finally:
        await dp.fsm.storage.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
