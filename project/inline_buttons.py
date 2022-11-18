from pyrogram.types import InlineKeyboardButton

initial_buttons = [
    [
        InlineKeyboardButton(
            "Add a new channel",
            callback_data="1 create",
        ),
        InlineKeyboardButton("Check current channels", callback_data="1 check"),
        InlineKeyboardButton("List of current channels", callback_data="1 current"),
    ]
]
