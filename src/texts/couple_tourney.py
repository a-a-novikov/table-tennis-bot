from constants import MONTHS
from utils.text_formatters import parse_int_to_emoji_int

ACCEPTOR_SELECTION = "Кому Вы бросите вызов?"
ACCEPTOR_SELECTED = ("Вы будете играть с {acceptor}.\n"
                     "До скольки побед будет продолжаться дуэль?")
TOURNEY_REGISTERED = ("Соперник извещен об объявленной дуэли! "
                      "Событие начнется после подтверждения с его стороны 🪑\n"
                      "Подробности о дуэли см. в кнопке под клавиатурой⬇️")
ACCEPTION_REQUEST = "{initiator} пригласил Вас на дуэль 👋"
TOURNEY_ACCEPTED = ("<b>Стартовала дуэль</b>\n"
                    "\n"
                    "{initiator}\n"
                    "🆚\n"
                    "{acceptor}!\n"
                     "Удачи участникам!\n"
                    "\n"
                    "Подробности о дуэли см. в кнопке под клавиатурой⬇️")
TOURNEY_DECLINED = ("<b>Дуэль была отклонена одним из участников</b>\n"
                    "\n"
                    "{initiator}\n"
                    "🆚\n"
                    "{acceptor}\n")
TOURNEY_MANUALLY_FINISHED = ("<b>Дуэль была прервана одним из участников</b>\n"
                             "\n"
                             "{initiator}\n"
                             "🆚\n"
                             "{acceptor}")
ALREADY_IN_ACTIVE_TOURNEY = "Ошибка при регистрации дуэли. Вы уже участвуете в другой дуэли."
TOURNEY_GAME_RESULT_SELECTION = "Кто вытащил катку?"
TOURNEY_GAME_RESULT_RECORDED = ("<b>Записан результат дуэльной партии!</b>\n"
                                "\n"
                                "Положение дел таково:\n"
                                "{player1_wins} {player1}\n"
                                "🆚\n"
                                "{player2_wins} {player2}")
TOURNEY_FINISHED = ("🎊<b>Дуэль завершена</b>🎊\n"
                   "\n"
                   "Победу одержал <b>{winner}</b>, выиграв {winner_wins} игр, поздравляем машину!!!\n"
                   "\n"
                   "<b>{loser}</b> не дотянул совсем чуть-чуть, взяв верх в {looser_wins} играх!")
CHOOSE_TROPHY_POKY_BALL = ("В качестве награды за победу, "
                           "Вы можете взять себе один из poky-ball'ов поверженного дуэлянта")
TROPHY_POKY_BALL_RETRIEVED = "Вы получили poky-ball {emoji}!"
POKY_BALL_LOST = "Вы утратили poky-ball {emoji} - победитель дуэли выбрал его в качестве трофея!"


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
        initiator_wins=parse_int_to_emoji_int(initiator_wins),
        acceptor=acceptor_name,
        acceptor_wins=parse_int_to_emoji_int(acceptor_wins),
    )
