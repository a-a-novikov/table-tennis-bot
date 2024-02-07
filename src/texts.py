from constants import MONTHS
from helpers import int_to_emoji_int

WELCOME_TEXT = ("Бот настольного тенниса приветствует Вас!\n"
                "Участвуйте в after-daily играх и организуйте собственные дуэли!")

REGISTRATION_ANNOUNCE = "Сбор заявок на after-daily теннис ({date}):"

REGISTRATION_CONFIRMED = ("Сбор заявок на after-daily теннис ({date}):\n"
                         "\n"
                         "✅Вы участвуете ✅")

REGISTRATION_DECLINED = ("Сбор заявок на after-daily теннис ({date}):\n"
                         "\n"
                         "😔Вы пропускаете 😔")

MARK_GAME_RESULT = "Как прошла after-daily партия?"

WON_RESULT_MARKED = ("Поздравляем с победой! Сегодня Вы - машина 🚘\n"
                     "*результат записан*")

LOOSE_RESULT_MARKED = ('«Победа - это не главное. Главное - это мир и гармония» - Чжуан-цзы ☯️\n'
                       "*результат записан*")

SKIPPED_RESULT_MARKED = "Это печально😢. Ждем Вас на новых играх!"


ACCEPTOR_SELECTION = "Кому Вы бросите вызов?"


ACCEPTOR_SELECTED = ("Вы будете играть с {acceptor}.\n"
                     "До скольки побед будет продолжаться дуэль?")

TOURNEY_REGISTERED = ("Соперник извещен об объявленной дуэли! "
                      "Событие начнется после подтверждения с его стороны 🪑\n"
                      "Подробности о дуэли см. в кнопке под клавиатурой⬇️")

ACCEPTION_REQUEST = "{initiator} пригласил Вас на дуэль 👋"


TOURNEY_ACCEPTED = ("Стартовала дуэль {initiator} 🆚 {acceptor}!\n"
                     "Удачи участникам!\n"
                    "\n"
                    "Подробности о дуэли см. в кнопке под клавиатурой⬇️")


TOURNEY_DECLINED = "Дуэль {initiator} 🆚 {acceptor} была отклонена одним из участников ☠️"

TOURNEY_MANUALLY_FINISHED = "Дуэль {initiator} 🆚 {acceptor} была прервана одним из участников ☠️"


ALREADY_IN_ACTIVE_TOURNEY = "Ошибка при регистрации дуэли. Вы уже участвуете в другой дуэли."

TOURNEY_GAME_RESULT_SELECTION = "Кто вытащил катку?"

TOURNEY_GAME_RESULT_RECORDED = ("<b>Записан результат дуэльной партии!</b>\n"
                                "\n"
                                "Положение дел таково:\n"
                                "{player1_wins} {player1}\n"
                                "🆚\n"
                                "{player2_wins} {player2}")


TOURNEY_FINISHED = ("🎊Дуэль завершена🎊\n"
                   "\n"
                   "Победу одержал <b>{winner}</b>, выиграв {winner_wins} игр, поздравляем машину!!! 🚗💪🥳\n"
                   "\n"
                   "<b>{loser}</b> недотянул совсем чуть-чуть, взяв верх в {looser_wins} играх!")


PERSONAL_STATISTICS = ("📊<b>Ваша статистика:</b>\n"
                      "\n"
                      "Дата последней after-daily партии: {last_daily_game_date}\n"
                      #Самый длинный стрик"
                      "After-daily партий выиграно (всего партий): {daily_wins} ({daily_total})\n"
                      "Дуэльных партий выиграно (всего партий): {couple_tourney_games_won} ({couple_tourney_games_total})\n"
                      "Дуэлей выиграно (всего дуэлей): {couple_tourney_won} ({couple_tourney_total})")


PATCH_NOTE = ("Обновление бота v{version}🔥\n"
              "\n"
              "{content}")


def get_current_tourney_info(
    wins_total: int,
    day: int,
    month: int,
    initiator_name: str,
    initiator_wins: int,
    acceptor_name: str,
    acceptor_wins: int,
) -> str:
    template = ("<b>Дуэль на {wins_total} побед</b>\n\n"
                "Дата начала: {day} {month}\n\n"
                "{initiator_wins} {initiator}\n"
                "🆚\n"
                "{acceptor_wins} {acceptor}")
    return template.format(
        wins_total=wins_total,
        day=day,
        month=MONTHS[month],
        initiator=initiator_name,
        initiator_wins=int_to_emoji_int(initiator_wins),
        acceptor=acceptor_name,
        acceptor_wins=int_to_emoji_int(acceptor_wins),
    )


def format_pairs_list(pairs: list[list[str, str]]) -> str:
    result = "<b>Сегодня играют:</b>\n\n"
    order = 1
    for p1, p2 in pairs:
        result += f"{order}. {p1} 🆚 {p2}\n"
        order += 1
    return result
