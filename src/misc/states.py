from aiogram.fsm.state import StatesGroup, State


class AdminStates:
    class MailingPostCreating(StatesGroup):
        wait_for_content_message = State()
        wait_for_button_data = State()
        wait_for_confirm = State()

    class ReferralLinksAdding(StatesGroup):
        wait_for_name = State()


class BandCreationStates(StatesGroup):
    enter_band_title = State()


class ActivateBonusStates(StatesGroup):
    wait_for_code = State()


class BandEditStates(StatesGroup):
    edit_band_title = State()
    consider_delete_band = State()


class EnterBetStates(StatesGroup):
    wait_for_bet_amount = State()


class EnterEvenUnevenBetStates(StatesGroup):
    wait_for_bet = State()


class AutoDepositStates(StatesGroup):
    wait_for_amount = State()


class HalfAutoDepositStates(StatesGroup):
    wait_for_amount = State()
    wait_for_screenshot = State()


class HalfAutoWithdrawStates(StatesGroup):
    wait_for_amount = State()
    wait_for_requisites = State()
    wait_for_confirm = State()
