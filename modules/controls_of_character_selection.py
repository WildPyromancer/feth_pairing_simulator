from typing import NamedTuple, Any
import os

import flet as ft
from flet_core.types import (
    OptionalEventCallable,
)

from . import character as ch

IMAGE_BLEND_COLOR = ft.colors.GREY_900


class ExistenceColumnParts(NamedTuple):
    row: ft.Row
    image: ft.Image
    checkbox: ft.Checkbox


def get_existence_column_parts(
    ct: ch.UniqueCharactersTuple,
    on_change_check_box: OptionalEventCallable[Any],
    images_dir: str,
) -> list[ExistenceColumnParts]:
    _: list[ExistenceColumnParts] = []
    for c in ct:
        checkbox = ft.Checkbox(
            label=c.DATA.NAME,
            value=c.state.exist,
            on_change=on_change_check_box,
        )
        image = ft.Image(
            src=os.path.join(images_dir, f"{c.DATA.NAME}.png"),
            color=None if c.state.exist else IMAGE_BLEND_COLOR,
            color_blend_mode=ft.BlendMode.COLOR,
        )
        row = ft.Row(col={"sm": 6, "md": 4, "xxl": 2}, controls=[image, checkbox])
        _.append(ExistenceColumnParts(row, image, checkbox))
    return _
