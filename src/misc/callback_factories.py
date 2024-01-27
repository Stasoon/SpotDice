from typing import Optional, Literal

from aiogram.filters.callback_data import CallbackData

from .enums import DepositMethod, WithdrawMethod, GameType, GameCategory
from .enums.leagues import BandLeague


class BlackJackCallback(CallbackData, prefix='BJ'):
    """
    game_number: int \n
    move: Literal['take', 'stand']
    """
    game_number: int
    move: Literal['take', 'stand']


class MinesCreationCallback(CallbackData, prefix='mines_creation'):
    mines_count: int
    bet: float
    action: str


class MinesCallback(CallbackData, prefix='mines_gameplay'):
    """
    x: int
    y: int
    is_mine: Literal['True', 'False']
    is_opened: Literal['True', 'False']
    """
    x: int
    y: int
    is_mine: Literal['True', 'False']
    is_opened: Literal['True', 'False']

    @staticmethod
    def from_string(data: str):
        try:
            x, y, is_mine, is_opened = data.split(':')[1:]
            return MinesCallback(x=int(x), y=int(y), is_mine=is_mine, is_opened=is_opened)
        except ValueError:
            return None


class GamesCallback(CallbackData, prefix="games"):
    """
    action: str  \n
    game_number: Optional[int] = None  \n
    game_category: Optional[GameCategory] = None  \n
    game_type: Optional[GameType] = None
    """
    action: Literal['create', 'show', 'confirm', 'refresh', 'stats', 'cancel', 'join']
    game_number: Optional[int] = None
    game_category: Optional[GameCategory] = None
    game_type: Optional[GameType] = None


class GamePagesNavigationCallback(CallbackData, prefix='games_nav'):
    direction: Literal['prev', 'next']
    category: GameCategory
    current_page: int = 0


class BandCallback(CallbackData, prefix='band'):
    """ Управление своей бандой """
    band_id: int
    action: Optional[str] = None


class BandsMapCallback(CallbackData, prefix='bands_map'):
    league: BandLeague
    current_league: Optional[BandLeague] = None


class BandMemberCallback(CallbackData, prefix='band_member'):
    """ Управление участниками банды """
    band_id: int
    user_id: int
    action: str = 'kick'


class MenuNavigationCallback(CallbackData, prefix="nav"):
    """
    Отвечает за навигацию в основных ветках меню. Если option не задана, возврат в ветку
    branch: str
    option: Optional[str] = None
    """
    branch: str  # play / profile / info / ...
    option: Optional[str] = None


class WithdrawCallback(CallbackData, prefix='withdraw'):
    """Отвечает за выбор метода пополнения/депозита"""
    method: WithdrawMethod
    currency: Optional[str] = None


class DepositCallback(CallbackData, prefix='deposit'):
    """Отвечает за выбор метода пополнения/депозита"""
    method: DepositMethod
    currency: Optional[str] = None


class DepositCheckCallback(CallbackData, prefix='check_payment'):
    """Отвечает за кнопку проверки платежа при автооплате"""
    method: DepositMethod
    invoice_id: int


class ConfirmWithdrawRequisitesCallback(CallbackData, prefix='confirm_withdraw_requisites'):
    """
    Отвечает за подтверждение отправки запроса на вывод средств \n
    requisites_correct: bool
    """
    requisites_correct: bool


class AdminValidatePaymentCallback(CallbackData, prefix='confirm_payment'):
    """
    Отвечает за отклонение или подтверждение оплаты у админа \n
    user_id: int \n
    amount: float \n
    transaction_type: Literal['deposit', 'withdraw'] \n
    confirm: bool
    """
    user_id: int
    amount: float
    transaction_type: Literal['deposit', 'withdraw']
    method: DepositMethod | WithdrawMethod
    confirm: bool


class ReferralLinkCallback(CallbackData, prefix='referral_link'):
    action: str
    link_id: Optional[int] = None


class PromoCodeCallback(CallbackData, prefix=''):
    promo_code_id: int
    action: str
