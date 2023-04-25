import telebot

from bot.config import Config, FACULTIES, OTHER_PROBLEMS

keyboard = lambda: telebot.types.ReplyKeyboardMarkup(True, True)


def start_keyboard():
    kb = keyboard()
    kb.row(Config.i_have_question_button)
    return kb


def problem_keyboard():
    kb = keyboard()
    kb.row(Config.faculty_button)
    kb.row(Config.no_faculty_button)
    return kb


def faculty_keyboard():
    kb = keyboard()
    for faculty in FACULTIES:
        kb.row(faculty)
    kb.row(Config.rollback)
    return kb


def yes_no_keyboard():
    kb = keyboard()
    kb.row(Config.yes)
    kb.row(Config.no)
    kb.row(Config.rollback)
    return kb


def other_problems_keyboard():
    kb = keyboard()
    for problem in OTHER_PROBLEMS:
        kb.row(problem)
    kb.row(Config.rollback)
    return kb


def finish_dialog_keyboard():
    kb = keyboard()
    kb.row(Config.finish_dialog)
    return kb
