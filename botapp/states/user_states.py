from aiogram.fsm.state import State, StatesGroup

class UserStates(StatesGroup):
    """User states for different scenarios"""
    MAIN_MENU = State()
    WAITING_FOR_NAME = State()
    WAITING_FOR_CONTACT = State()
    REGISTRATION_COMPLETE = State()