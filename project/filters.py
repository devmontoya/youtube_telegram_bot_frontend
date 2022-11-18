from pyrogram import filters


def main_filter_deco(user_states):
    async def func(flt, _, message):
        user_id = str(message.chat.id)
        return (
            not (user_id in user_states.keys())
            or user_states[user_id] == 0
            or message.text == "/start"
        )

    return filters.create(func)


def state_filter_query(user_states, state, expected_id):  # TODO
    async def func(flt, _, query):
        user_id = str(query.message.chat.id)
        print(query.data[0])
        return user_states[user_id] == state and query.data[0] == str(expected_id)

    return filters.create(func)


def state_filter_message(user_states, state):
    async def func(flt, _, message):
        user_id = str(message.chat.id)
        return user_states[user_id] == state

    return filters.create(func)
