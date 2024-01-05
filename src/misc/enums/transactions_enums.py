from enum import Enum


class DepositMethod(str, Enum):
    CRYPTO_BOT = 'КриптоБот'
    SBP = 'СБП'
    U_MONEY = 'ЮMoney'
    QIWI = 'Киви'


class WithdrawMethod(str, Enum):
    CRYPTO_BOT = 'КриптоБот'
    SBP = 'СБП'
    U_MONEY = 'ЮMoney'


class BonusType(Enum):
    ON_BALANCE = 'on_balance'
