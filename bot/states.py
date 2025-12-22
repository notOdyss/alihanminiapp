from aiogram.fsm.state import StatesGroup, State

class TransactionStates(StatesGroup):
    amount_input = State()
