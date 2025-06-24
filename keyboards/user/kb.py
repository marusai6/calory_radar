from aiogram import types

user_menu = types.InlineKeyboardMarkup(inline_keyboard=[
    [types.InlineKeyboardButton(
        text="Да",
        callback_data="Yes"),
        types.InlineKeyboardButton(
        text="Нет",
        callback_data="No")],
])