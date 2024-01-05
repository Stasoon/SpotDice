from aiogram import Bot
from aiogram.types import InputFile

from src.database import games, Game


class GameMessageSender:
    def __init__(self, bot: Bot, game: Game):
        self.bot = bot
        self.game = game

    async def __send_message(self, chat_id, text, photo, markup):
        if photo:
            await self.bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=text,
                reply_markup=markup,
                parse_mode='HTML'
            )
        else:
            await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=markup,
                parse_mode='HTML'
            )

    async def send(
            self,
            text: str = None,
            photo: str | InputFile = None,
            markup=None,
            player_ids: list[int] = None
    ):
        """
        Отправляет сообщения игрокам
        Если игра создана в чате - отсылает в чат, иначе по личкам
        Если указать player_ids, рассылка будет только по ним. Иначе по всем участникам игры
        """
        if self.game.chat_id < 0:
            await self.__send_message(chat_id=self.game.chat_id, text=text, photo=photo, markup=markup)
        else:
            player_ids = player_ids if player_ids else await games.get_player_ids_of_game(self.game)
            [await self.__send_message(player_id, text, photo, markup) for player_id in player_ids]
