REGISTRATION_ANNOUNCE = "Сбор заявок на after-daily теннис ({date}):"
REGISTRATION_CONFIRMED = ("Сбор заявок на after-daily теннис ({date}):\n"
                         "\n"
                         "✅Вы участвуете ✅")
REGISTRATION_DECLINED = ("Сбор заявок на after-daily теннис ({date}):\n"
                         "\n"
                         "😔Вы пропускаете 😔")
TOO_LITTLE_BOOKINGS_FOR_AFTER_DAILY = ("After-daily теннис не состоится, "
                                       "т.к. Ваша заявка сегодня - единственная 😭")
MARK_GAME_RESULT = "Как прошла after-daily партия?"
WON_RESULT_MARKED = ("Поздравляем с победой! Сегодня Вы - машина 🚘\n"
                     "*результат записан*")
LOOSE_RESULT_MARKED = ('«Победа - это не главное. Главное - это мир и гармония» - Чжуан-цзы ☯️\n'
                       "*результат записан*")
SKIPPED_RESULT_MARKED = "Это печально😢. Ждем Вас на новых играх!"


def format_pairs_list(pairs: list[list[str, str]]) -> str:
    result = "<b>Сегодня играют:</b>\n\n"
    order = 1
    for p1, p2 in pairs:
        result += f"{order}. {p1} <b>VS</b> {p2}\n"
        order += 1
    return result
