from aiogram import html, types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message

from base_machine import BaseMachine
from machines_manager import MachinesManager


class Form(BaseMachine):
    states = ["initial", "name", "save_name", "age", "save_age", "gender", "show"]
    transitions = [
        ["proceed", "initial", "name"],
        ["proceed", "name", "save_name"],
        ["proceed", "save_name", "age"],
        ["proceed", "age", "save_age"],
        ["proceed", "save_age", "gender"],
        ["proceed", "gender", "show"],
    ]

    def __init__(self, *args, machines_manager: MachinesManager = None, **kwargs):
        super().__init__(self, *args, machines_manager=machines_manager, **kwargs)

    async def on_enter_name(self, message: Message, state: FSMContext):
        await message.answer("Hi there! What's your name?")

    async def on_enter_save_name(self, message: Message, state: FSMContext):
        await state.update_data(name=message.text)
        await self.proceed(message, state)

    async def on_enter_age(self, message: Message, state: FSMContext):
        await message.answer("How old are you?")

    async def on_enter_save_age(self, message: Message, state: FSMContext):
        if not message.text.isdigit():
            await message.answer("Age gotta be a number.\n")
            await self.to_age(message, state)
            return

        await state.update_data(age=message.text)
        await self.proceed(message, state)

    async def on_enter_gender(self, message: Message, state: FSMContext):
        markup = types.ReplyKeyboardMarkup(
            keyboard=[
                [
                    types.KeyboardButton(text="Male"),
                    types.KeyboardButton(text="Female"),
                ],
                [types.KeyboardButton(text="Other")],
            ],
            resize_keyboard=True,
            selective=True,
        )

        await message.answer("What is your gender?", reply_markup=markup)

    async def on_enter_show(self, message: Message, state: FSMContext):
        if message.text not in ("Male", "Female", "Other"):
            await message.answer(
                "Bad gender name. Choose your gender from the keyboard."
            )
            await self.to_gender(message, state)
            return

        await state.update_data(gender=message.text)
        data = await state.get_data()
        await message.answer(
            f"Hi! Nice to meet you {html.quote(data['name'])}\n"
            f"Age: {html.code(data['age'])}\n"
            f"Gender: {data['gender']}",
            parse_mode="HTML",
        )

        await self.finish(state)
