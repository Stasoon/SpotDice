from aiogram import html


def format_float_digits(value: float) -> str:
    """Возвращает строку с value, у которого два знака после запятой"""
    return f"{value:.2f}"


def format_float_to_rub_string(value: float, use_html: bool = True) -> str:
    """Возвращает строку с amount с двумя знаками после запятой и добавлением знака рубля.  \n
    При use_html = True применяет тег <code>"""
    balance_text = f"{ format_float_digits(value) } ₽"
    return html.code(balance_text) if use_html else balance_text
