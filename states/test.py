from aiogram.filters.state import StatesGroup, State


class Test(StatesGroup):
    Q1 = State()
    Q2 = State()


class AdminState(StatesGroup):
    are_you_sure = State()
    ask_ad_content = State()
    add_admin = State()
    remove_admin = State()
    reply_user = State()


class UserState(StatesGroup):
    waiting_feedback = State()
