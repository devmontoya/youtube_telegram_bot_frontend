from filters import main_filter_deco, state_filter_message, state_filter_query
from infra.http_client import HTTPClient
from inline_buttons import initial_buttons
from logger import log
from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup
from schemas.user import User


class UserState:
    user_states = {}  # Stores users' state
    id_cache = {}

    @classmethod
    async def get_id_db(cls, chat_id_telegram: str):
        try:
            id_db = cls.id_cache[chat_id_telegram]
        except KeyError:
            log.info("User no found in cache")
            async with HTTPClient() as http_client:
                response = await http_client.get(
                    url="/api_front/get_client_id", id_element=chat_id_telegram
                )
                if response.status == 404:
                    log.info("User no found in DB")
                    new_user = User(chat_id=chat_id_telegram)
                    response = await http_client.post(
                        url="/api_front/add_new_client", data=new_user.dict()
                    )
                    log.info("New user added")
                    print(response.element)
                id_db = (response.element)["client_id"]
            cls.id_cache[chat_id_telegram] = id_db
        return id_db


@Client.on_message(main_filter_deco(UserState.id_cache))
async def menu(client, message):  # State zero
    user_id = str(message.chat.id)
    user_id_response ="Hello user: " + "*"*(len(user_id)-4) + user_id[-4:]
    _ = await message.reply(
        user_id_response, reply_markup=InlineKeyboardMarkup(initial_buttons)
    )
    await UserState.get_id_db(user_id)

    UserState.user_states[user_id] = 1  # Change the user's state


# Case new channel
@Client.on_callback_query(
    state_filter_query(UserState.user_states, state=1, expected_tag="1 create")
)
async def state_one_add_channel(client, callback_query):
    user_id_tlm = str(callback_query.message.chat.id)
    await callback_query.edit_message_text(
        "Enter the url of a channel you want to be following"
    )
    UserState.user_states[user_id_tlm] = 2


@Client.on_message(state_filter_message(UserState.user_states, state=2))
async def url_input(client, message):
    user_id_tlm = str(message.chat.id)
    user_id = await UserState.get_id_db(user_id_tlm)
    print(user_id)
    # Early URL validity test
    if (
        message.text[:16] == "www.youtube.com/"
        or message.text[:24] == "https://www.youtube.com/"
    ):
        await message.reply(f"Entered URL '{message.text}'\nWait please...")
        new_client_channel_request = {"client_id": user_id, "url": message.text}
        async with HTTPClient() as http_client:
            response = await http_client.post(
                url="/api_front/new_client_channel", data=new_client_channel_request
            )
        new_videos = response.element["list_videos"]
        response_message = "New videos:\n"
        for video in new_videos:
            response_message += f"- [{video[0]}](www.youtube.com{video[1]})\n"
        await message.reply(response_message)
    else:
        await message.reply("Invalid URL\nPlease try again")


# Case new channel
@Client.on_callback_query(
    state_filter_query(UserState.user_states, state=1, expected_tag="1 current")
)
async def state_one_current_list(client, callback_query):
    user_id_tlm = str(callback_query.message.chat.id)
    user_id = await UserState.get_id_db(user_id_tlm)
    async with HTTPClient() as http_client:
        response = await http_client.get(
            f"/api_front/get_clients_channel_list/{user_id}"
        )
    channel_list = (response.element)["channel_list"]

    result_text = "Channels you are following right now:\n"
    for i, channel in enumerate(channel_list):
        result_text += f"{i+1}. [{channel['channel_name']}]({channel['channel_url']})\n"

    await callback_query.edit_message_text(result_text)
    UserState.user_states[user_id] = 0


# Case new channel
@Client.on_callback_query(
    state_filter_query(UserState.user_states, state=1, expected_tag="1 check")
)
async def state_one_check_channels(client, callback_query):
    user_id_tlm = str(callback_query.message.chat.id)
    user_id = await UserState.get_id_db(user_id_tlm)
    async with HTTPClient() as http_client:
        response = await http_client.get(
            f"/api_front/get_clients_channel_list/{user_id}"
        )
    channel_list = (response.element)["channel_list"]
    log.debug("app got channels")
    result_text = "Channels you are following right now:\n"
    for i, channel in enumerate(channel_list):
        result_text += (
            f"\n{i+1}. [{channel['channel_name']}]({channel['channel_url']})\n"
        )
        new_client_channel_request = {
            "client_id": user_id,
            "url": f"www.youtube.com/c/{channel['channel_name']}",
        }  # TODO is better to use channel_id, it requires a new endpoint
        async with HTTPClient() as http_client:
            response = await http_client.post(
                url="/api_front/new_client_channel", data=new_client_channel_request
            )
        new_videos = response.element["list_videos"]
        for video in new_videos:
            result_text += f"- [{video[0]}](www.youtube.com{video[1]})\n"
        if len(new_videos) == 0:
            result_text += "No new videos for this channel\n"
    await callback_query.edit_message_text(result_text)
    UserState.user_states[user_id] = 0
