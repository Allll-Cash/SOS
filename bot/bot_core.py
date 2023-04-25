from telebot.types import Message, ReplyKeyboardRemove

import bot.keyboards as kb
from bot.config import Config, FACULTIES, OTHER_PROBLEMS
from bot.management.commands.bot import bot
from bot.models import Student, TelegramMessage, Request


def select_role(destination):
    if destination in FACULTIES.values():
        return "представителем студсовета"
    if destination == "campus":
        return "социальным комитетом"
    if destination == "dormitory":
        return "комитетом по общежитиям"
    if destination == "education":
        return "комитетом по качеству образования"
    if destination == "foreign":
        return "комитетом по внешним коммуникациям"
    return "оператором"


class Core:

    client: Student

    def __init__(self, message: Message):
        self.message = message
        self.student, _ = Student.objects.get_or_create(telegram_id=message.chat.id)
        self.student.telegram_name = message.from_user.full_name
        self.student.telegram_username = message.from_user.username or ""
        self.message_text = message.text or message.caption or ""

    def handle_default(self):
        raise NotImplementedError(f"No handler for state {self.client.state}")

    def send_message(self, text: str, reply_markup=None, remove_keyboard=True):
        if reply_markup is None and remove_keyboard:
            reply_markup = ReplyKeyboardRemove()
        bot.send_message(self.student.telegram_id, text, reply_markup=reply_markup)

    def process(self):
        method_name = f"handle_state_{self.student.state}"
        if self.message_text.lower() == "рестарт" or self.message_text.lower() == "restart":
            self.send_message("рестарчусь")
            self.client.delete()
            return
        if self.message_text.startswith('/'):
            method_name = f"handle_command_{self.message_text[1:]}"
        func = getattr(self, method_name, self.handle_default)
        func()
        self.student.save()

    def handle_command_start(self):
        last_request = self.student.last_request
        if last_request is not None:
            last_request.status = 2
            last_request.save()
        self.handle_state_new()

    def handle_state_manager(self):
        request = self.student.last_request
        if self.message_text == Config.finish_dialog:
            request.status = 2
            self.send_message(Config.dialog_finished, reply_markup=kb.start_keyboard())
            self.student.set_state("start")
            request.save()
        else:
            message = TelegramMessage.objects.create(request=request, text=self.message_text)
            message.attach_photo(self.message)

    def handle_state_new(self):
        self.send_message(Config.hello, reply_markup=kb.start_keyboard())
        self.student.set_state("start")

    def handle_state_start(self):
        if self.message_text == Config.i_have_question_button:
            self.send_message(Config.what_problem, reply_markup=kb.problem_keyboard())
            self.student.set_state("problem")
        else:
            self.send_message(Config.use_buttons, reply_markup=kb.start_keyboard())

    def handle_state_problem(self):
        if self.message_text == Config.faculty_button:
            self.send_message(Config.select_your_faculty, reply_markup=kb.faculty_keyboard())
            self.student.set_state("select_faculty")
        elif self.message_text == Config.no_faculty_button:
            self.send_message(Config.select_problem, reply_markup=kb.other_problems_keyboard())
            self.student.set_state("select_other_problem")
        else:
            self.send_message(Config.use_buttons, reply_markup=kb.problem_keyboard())

    def handle_state_select_faculty(self):
        if self.message_text == Config.rollback:
            self.send_message(Config.what_problem, reply_markup=kb.problem_keyboard())
            self.student.set_state("problem")
            return
        if self.message_text not in FACULTIES:
            self.send_message(Config.use_buttons, reply_markup=kb.faculty_keyboard())
        else:
            Request.objects.create(student=self.student, destination=FACULTIES[self.message_text])
            self.send_message(Config.want_to_be_anonymous, reply_markup=kb.yes_no_keyboard())
            self.student.set_state("select_anonymous")

    def handle_state_select_anonymous(self):
        if self.message_text not in (Config.yes, Config.no, Config.rollback):
            self.send_message(Config.use_buttons, reply_markup=kb.yes_no_keyboard())
        elif self.message_text == Config.rollback:
            if self.student.previous_state == "select_other_problem":
                self.send_message(Config.select_problem, reply_markup=kb.other_problems_keyboard())
            else:
                self.send_message(Config.select_your_faculty, reply_markup=kb.faculty_keyboard())
            self.student.rollback()
        else:
            req = self.student.last_request
            req.anonymous = self.message_text == Config.yes
            req.save()
            self.send_message(Config.connecting_with_manager.format(role=select_role(req.destination)), reply_markup=kb.finish_dialog_keyboard())
            self.student.set_state("manager")

    def handle_state_select_other_problem(self):
        if self.message_text == Config.rollback:
            self.send_message(Config.what_problem, reply_markup=kb.problem_keyboard())
            self.student.set_state("problem")
            return
        if self.message_text not in OTHER_PROBLEMS:
            self.send_message(Config.use_buttons, reply_markup=kb.other_problems_keyboard())
        else:
            Request.objects.create(student=self.student, destination=OTHER_PROBLEMS[self.message_text])
            self.send_message(Config.want_to_be_anonymous, reply_markup=kb.yes_no_keyboard())
            self.student.set_state("select_anonymous")
