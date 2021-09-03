import asyncio
import logging

import aiogram.types
from aiogram import Bot, Dispatcher
from aiogram.dispatcher.fsm.context import FSMContext
from transitions.extensions.asyncio import AsyncMachine

from form import Form
from transitions_filter import TransitionsFilter
from transitions_middleware import TransitionsMiddleware

logger = logging.getLogger(__name__)

BOT_TOKEN = "BOT_TOKEN"


async def start_form(
    message: aiogram.types.Message,
    state: FSMContext,
):
    form_machine = Form()
    await state.update_data(machine=form_machine)
    await form_machine.proceed(message, state)  # start machine


async def machine(
    message: aiogram.types.Message,
    machine: AsyncMachine,
    state: FSMContext,
):
    await machine.proceed(message, state)  # next states


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()

    dp.update.outer_middleware(TransitionsMiddleware())
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
