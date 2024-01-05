from random import randint

from PIL import Image, ImageDraw, ImageFont
from PIL.Image import BICUBIC, HAMMING
from aiogram.types import BufferedInputFile

from src.database import Game
from src.database.games import playing_cards, game_scores
from .base_painter import _GameImagePainter


class BaccaratImagePainter(_GameImagePainter):
    def __init__(self, game: Game):
        super().__init__(game)

        self.cards_x_spacing = self.card_size[0] - 110
        self.cards_y_spacing = self.card_size[1] // 5

        self.points_font = ImageFont.truetype("resources/fonts/font.otf", 45, encoding='UTF-8')

    async def __draw_tokens(self, table: Image):
        token_size = (80, 80)

        # координаты полей по Y
        fields_y_positions = [265, 350, 435]

        moves = sorted(move.value for move in await game_scores.get_game_moves(game=self.game))

        for n, pos in enumerate(fields_y_positions, start=1):
            token_count = moves.count(n)
            used_positions = []
            # Отрисовка фишек
            for _ in range(token_count):
                while True:
                    random_x_pos = randint(500, 700)  # Или другой диапазон, какой вам нужен
                    if all(abs(random_x_pos - pos) >= 20 for pos in used_positions):
                        used_positions.append(random_x_pos)
                        break
                random_rotation = randint(0, 360)

                with Image.open('resources/cards/token.png') as token_img:
                    token_img = token_img.resize(token_size, resample=HAMMING)
                    token_img = token_img.rotate(random_rotation, expand=True, resample=BICUBIC)
                    table.paste(token_img, (random_x_pos, pos), token_img)  # IDE ругается на pos, но всё нормально

    async def __draw_player_cards_and_points(self, start_y_pos: int):
        start_x_left = 50
        player_points = await playing_cards.count_player_score(game_number=self.game.number, player_id=1) % 10
        text = f"ИГРОК\n{player_points}"

        # рисуем текст с очками игрока
        self.draw.text(
            xy=(start_x_left + 5, (self.table_size[1] - self.card_size[1]) // 2 + 100 + 300),
            text=text,
            fill=(255, 255, 0, 230),
            font=self.points_font,
            align='center'
        )
        # рисуем карты игрока
        player_cards = await playing_cards.get_player_cards(game_number=self.game.number, player_id=1)
        for n, card in enumerate(player_cards):
            with Image.open('resources/cards/' + f"{card.value}{card.suit}" + '.png') as card_img:
                card_img = card_img.resize(self.card_size)

                x = start_x_left + n * self.cards_x_spacing
                y = start_y_pos + n * self.cards_y_spacing

                self.table.paste(card_img, (x, y), card_img)

    async def __draw_banker_cards_and_points(self, start_y_pos: int):
        start_x_right = self.table_size[0] - self.card_size[0] - 50

        # Рисуем очки дилера
        banker_points = await playing_cards.count_dealer_score(game_number=self.game.number) % 10
        self.draw.text(
            xy=(start_x_right - 20, (self.table_size[1] - self.card_size[1]) // 2 + 100 + 300),
            text=f"БАНКИР\n{banker_points}",
            fill=(255, 255, 0, 230),
            font=self.points_font,
            align='center'
        )
        # рисуем карты дилера
        banker_cards = await playing_cards.get_dealer_cards(game_number=self.game.number)
        for n, card in enumerate(banker_cards):
            with Image.open('resources/cards/' + f"{card.value}{card.suit}" + '.png') as card_img:
                card_img = card_img.resize(self.card_size)

                x = start_x_right - n * self.cards_x_spacing
                y = start_y_pos + n * self.cards_y_spacing

                self.table.paste(card_img, (x, y), card_img)

    async def get_image(self) -> BufferedInputFile:
        with Image.open('resources/cards/baccarat_table.png') as table:
            self.table = table
            self.table_size = table.size

            self.draw = ImageDraw.Draw(table)

            # рисуем заголовок
            self._draw_header(game_name='BACCARAT')

            # рисуем фишки
            await self.__draw_tokens(table)

            # вычисляем стартовую карт по вертикали
            player_cards = await playing_cards.get_player_cards(game_number=self.game.number, player_id=1)
            banker_cards = await playing_cards.get_dealer_cards(game_number=self.game.number)
            cards_count_vertical_offset = (
                28 if len(player_cards) == 3 or len(banker_cards) == 3
                else 0
            )
            start_y = (self.table_size[1] - self.card_size[1]) // 2 - cards_count_vertical_offset
            # рисуем карты и очки игрока
            await self.__draw_player_cards_and_points(start_y)
            # рисуем карты и очки банкира
            await self.__draw_banker_cards_and_points(start_y)

            # Возвращаем буфер с фото
            return self._get_buffered_file_from_generated_photo()
