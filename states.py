from aiogram.fsm.state import State, StatesGroup


class AddExpense(StatesGroup):
    waiting_description = State()
    waiting_amount = State()


class DeleteExpense(StatesGroup):
    waiting_choice = State()


class AdminSettings(StatesGroup):
    waiting_week = State()
    waiting_month = State()
