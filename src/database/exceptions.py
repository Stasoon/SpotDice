from .models import User


class UserNotFound(Exception):
    def __init__(self, telegram_id: int | str):
        self.telegram_id = telegram_id

    def __str__(self):
        return f"Юзер с id {self.telegram_id} не найден!"


class BandNotFound(Exception):
    def __init__(self, band_id_or_title: int | str):
        self.band_id = band_id_or_title

    def __str__(self):
        return f"Банда с именем или id {self.band_id} не найдена!"


class BandTitleAlreadyTaken(Exception):
    def __init__(self, band_title: str):
        self.band_title = band_title

    def __str__(self):
        return f"Банда с именем {self.band_title} уже существует!"


class AlreadyInOtherBand(Exception):
    def __init__(self, user: User, band_id_or_title: str):
        self.user = user
        self.band_id_or_title = band_id_or_title

    def __str__(self):
        return f"Пользователь {self.user} {self.band_id_or_title = } уже является участником в другой банде!"
