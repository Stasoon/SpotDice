from typing import Collection

from src.database import PlayerScore
from src.messages.user.games.creatable_game_messages_base import CreatableGamesMessages
from src.misc.enums import BaccaratBettingOption


class BaccaratMessages(CreatableGamesMessages):
    @staticmethod
    def get_game_created(game_number: int):
        return f'🎴 Игра Baccarat №{game_number} создана!'

    @staticmethod
    def get_category_description(player_name: str) -> str:
        return '🎴 Baccarat'

    @staticmethod
    def ask_for_bet_amount(player_name: str) -> str:
        return None

    @staticmethod
    def get_bet_prompt() -> str:
        return 'Выберите, на чью победу хотите поставить:'

    @staticmethod
    async def get_baccarat_results(bet_choices: Collection[PlayerScore]):
        text = 'Результаты \n\n'
        for choice in bet_choices:
            text += f'{await choice.player.get()} — '
            match choice.value:
                case BaccaratBettingOption.PLAYER.value:
                    text += 'игрок \n'
                case BaccaratBettingOption.BANKER.value:
                    text += 'банкир \n'
                case BaccaratBettingOption.TIE.value:
                    text += 'ничья \n'
                case _:
                    text += 'пропустил ход'
        return text
