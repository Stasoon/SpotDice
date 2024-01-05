# from aiogram.filters import BaseFilter
# from aiogram.types import Message
#
#
# class CmdArgsStartsWithFilter(BaseFilter):
#     """
#     Проверяет, что аргументы команды начинаются с заданных символов.
#     Если проверка успешна, пробрасывает args с удалённым началом
#     """
#
#     def __init__(self, start_target_symbol: str):
#         self.target_symbol = start_target_symbol
#
#     async def __call__(self, message: Message) -> bool | dict:
#         # получаем текст аргумента команды
#         arg = message.text.split()[1:]
#
#         # если аргументов нет
#         if not arg or not arg[0].startswith(self.target_symbol):
#             return False
#
#         return {'args': arg[0].replace(self.target_symbol, '')}
