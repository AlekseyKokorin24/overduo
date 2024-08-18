from aiogram.fsm.state import StatesGroup, State


class FSM_FORM(StatesGroup):
    stateWaitingShopId = State() # Состояние ожидания ввода id магазина
    stateBeingInDB = State()
    stateWaitingInfoProducts = State()   # Состояние ожидания отправки фото, кода и годности
