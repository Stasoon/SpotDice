import random

from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup

from src.misc import GameType, GameCategory
from src.misc.callback_factories import (
    GamesCallback, MenuNavigationCallback, MinesCallback,
    MinesCreationCallback
)
from src.utils.text_utils import format_float_to_rub_string


class MinesKeyboards:
    quad_len = 5

    @staticmethod
    def get_create_or_back() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.button(text='Начать игру ▶', callback_data=MinesCreationCallback(mines_count=0, bet=0, action='create'))
        builder.button(text='🔙 Назад', callback_data=MenuNavigationCallback(branch='game_strategies'))

        builder.adjust(1)
        return builder.as_markup()

    @classmethod
    def get_creation(cls, mines_count: int, bet: float) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.button(text='Ставка:', callback_data='*')
        builder.button(text='➖', callback_data=MinesCreationCallback(mines_count=mines_count, bet=bet, action='-bet'))
        builder.button(text=f'{format_float_to_rub_string(bet, use_html=False)}', callback_data='*')
        builder.button(text='➕', callback_data=MinesCreationCallback(mines_count=mines_count, bet=bet, action='+bet'))
        builder.button(text='Min.', callback_data=MinesCreationCallback(mines_count=mines_count, bet=bet, action='minbet'))
        builder.button(text='÷2', callback_data=MinesCreationCallback(mines_count=mines_count, bet=bet, action='/2bet'))
        builder.button(text='x2', callback_data=MinesCreationCallback(mines_count=mines_count, bet=bet, action='*2bet'))
        builder.button(text='Max.', callback_data=MinesCreationCallback(mines_count=mines_count, bet=bet, action='maxbet'))

        builder.button(text='Количество мин:', callback_data='*')
        builder.button(text='➖', callback_data=MinesCreationCallback(mines_count=mines_count, bet=bet, action='-bombs'))
        builder.button(text=f'{mines_count} 🧨', callback_data='*')
        builder.button(text='➕', callback_data=MinesCreationCallback(mines_count=mines_count, bet=bet, action='+bombs'))
        builder.button(text='Min.',
                       callback_data=MinesCreationCallback(mines_count=mines_count, bet=bet, action='minbombs'))
        builder.button(text='÷2', callback_data=MinesCreationCallback(mines_count=mines_count, bet=bet, action='/2bombs'))
        builder.button(text='x2', callback_data=MinesCreationCallback(mines_count=mines_count, bet=bet, action='*2bombs'))
        builder.button(text='Max.',
                       callback_data=MinesCreationCallback(mines_count=mines_count, bet=bet, action='maxbombs'))

        builder.button(text=f'{cls.quad_len**2 - mines_count} 💎', callback_data='*')
        builder.button(text=f'ИГРАТЬ', callback_data=MinesCreationCallback(mines_count=mines_count, bet=bet, action='start'))
        builder.button(text=f'{mines_count} 🧨', callback_data='*')

        builder.button(
            text='🔙 Назад',
            callback_data=GamesCallback(action='show', game_category=GameCategory.MINES, game_type=GameType.MINES)
        )

        builder.adjust(1, 3, 4, 1, 3, 4, 3, 1, repeat=True)
        return builder.as_markup()

    @classmethod
    def get_hidden_mines(cls, mines_count: int, next_coefficient: float) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        mines_coordinates = random.sample(
            population=[(x, y) for x in range(cls.quad_len) for y in range(cls.quad_len)],
            k=mines_count
        )

        for i in range(cls.quad_len):
            for j in range(cls.quad_len):
                if (i, j) in mines_coordinates:
                    is_mine = True
                else:
                    is_mine = False

                builder.button(
                    text='❔',
                    callback_data=MinesCallback(x=i, y=j, is_mine=str(is_mine), is_opened=str(False))
                )

        builder.button(text=f'{cls.quad_len**2 - mines_count} 💎', callback_data='*')
        builder.button(text=f'1x', callback_data='*')
        builder.button(text=f'→', callback_data='*')
        builder.button(text=f'{next_coefficient:.2f}x', callback_data='*')
        builder.button(text=f'{mines_count} 🧨', callback_data='*')

        builder.button(text=f'💰 Забрать', callback_data=MinesCreationCallback(action='take_winning', mines_count=mines_count, bet=0))
        builder.adjust(*(cls.quad_len for _ in range(cls.quad_len)), 5, 1)
        return builder.as_markup()

    @classmethod
    def open_cell(cls, old_markup: InlineKeyboardMarkup, x: int, y: int):
        button = old_markup.inline_keyboard[x][y]
        data = MinesCallback.from_string(button.callback_data)

        button.text = '💎' if data.is_mine == str(False) else '🧨'
        button.callback_data = str(MinesCallback(x=x, y=y, is_mine=data.is_mine, is_opened='True'))

    @classmethod
    def update_opened_cells_count(cls, old_markup: InlineKeyboardMarkup, opened_count: int, mines_count: int):
        old_markup.inline_keyboard[cls.quad_len][0].text = f"{cls.quad_len ** 2 - opened_count - mines_count} 💎"

    @classmethod
    def update_coefficients(cls, old_markup: InlineKeyboardMarkup, current_coefficient: float, next_coefficient: float):
        old_markup.inline_keyboard[cls.quad_len][1].text = f"{current_coefficient:.2f}x"
        old_markup.inline_keyboard[cls.quad_len][3].text = f"{next_coefficient:.2f}x"

    @classmethod
    def update_current_winning(cls, old_markup: InlineKeyboardMarkup, winning_amount: float):
        new_text = f"💰 Забрать {format_float_to_rub_string(winning_amount, use_html=False)}"
        old_markup.inline_keyboard[cls.quad_len+1][0].text = new_text

    @classmethod
    def __get_button_text(cls, button, explosion_coordinates: tuple[int, int] = None):
        if button.text == '❔':
            data = MinesCallback.from_string(button.callback_data)
            if (int(data.x), int(data.y)) == explosion_coordinates:
                button_text = '💥'
            else:
                button_text = '🧨' if data.is_mine == 'True' else '🧊'
        else:
            button_text = button.text
        return button_text

    @classmethod
    def get_unlocked_field(
            cls, old_markup: InlineKeyboardMarkup,
            explosion_coordinates: tuple[int, int] = None
    ) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        for row in old_markup.inline_keyboard[:cls.quad_len]:
            for button in row:
                button_text = cls.__get_button_text(button=button, explosion_coordinates=explosion_coordinates)
                builder.button(text=button_text, callback_data='*')

        builder.button(text='🔄 Играть ещё раз', callback_data=MinesCreationCallback(mines_count=0, bet=0, action='create'))
        builder.button(text='🔙 В меню', callback_data=MenuNavigationCallback(branch='game_strategies'))
        builder.adjust(*(cls.quad_len for _ in range(cls.quad_len)), 1)
        return builder.as_markup()
