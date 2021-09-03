from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Update


class TransitionsMiddleware(BaseMiddleware[Update]):
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        fsm_context: FSMContext = data["state"]
        user_data = await fsm_context.get_data()

        data["machine"] = user_data.get("machine")
        result = await handler(event, data)
        user_data.update(machine=data["machine"])

        return result
