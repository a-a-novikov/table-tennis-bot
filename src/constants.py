MONTHS = ['', 'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
          'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']

EMOJI_BY_INT = {
    0: "0️⃣",
    1: "1️⃣",
    2: "2️⃣",
    3: "3️⃣",
    4: "4️⃣",
    5: "5️⃣",
    6: "6️⃣",
    7: "7️⃣",
    8: "8️⃣",
    9: "9️⃣",
}

BOT_METHODS_TO_RETRY_ASYNC = [
    "send_message",
    "delete_message",
    "get_chat",
    "edit_message_text",
    "answer_callback_query",
]

BOT_METHODS_TO_RETRY = []
