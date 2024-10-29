import flet as ft
from enum import IntEnum


class TextSize(IntEnum):
    small = 14
    medium = 16
    large = 22


class MyTextStyle(ft.TextStyle):
    def __init__(
        self,
        size: int = TextSize.medium.value,
        color: str = ft.colors.INVERSE_SURFACE,
    ):
        super().__init__(size=size, color=color)


class MyTextTheme(ft.TextTheme):
    def __init__(self):
        super().__init__()
        self.body_medium = MyTextStyle()


class MyTheme(ft.Theme):
    def __init__(self):
        super().__init__()
        self.text_theme = MyTextTheme()
        self.dialog_theme = ft.DialogTheme(
            title_text_style=MyTextStyle(size=TextSize.large.value),
            content_text_style=MyTextStyle(),
        )
