# coding: utf-8

import os
from typing import Any, Callable, Dict, Final, List, Tuple, NamedTuple

from flet_core.dropdown import Option
from flet_core.control_event import ControlEvent
import flet as ft
from flet_core.types import (
    OptionalEventCallable,
)

from . import character as ch


TEXT_STYLE_NONE: Final[ft.TextStyle] = ft.TextStyle(decoration=None)
TEXT_STYLE_LT: Final[ft.TextStyle] = ft.TextStyle(
    decoration=ft.TextDecoration.LINE_THROUGH, decoration_thickness=3
)

# 他からの参照無しなので、カプセル化したい。


def get_default_value_of_dd(character_has_solo_end: bool):
    if character_has_solo_end:
        return "ソロエンド"
    else:
        return "エンド無し"


def get_dropdown_text(pair_name: str, is_already_married: bool):
    return f'{"既" if is_already_married else "未"} {pair_name}'


def get_a_textstyle(
    character_name_of_row: str, marriage_partner_name_of_dd: str
) -> ft.TextStyle:
    if marriage_partner_name_of_dd == character_name_of_row:
        return TEXT_STYLE_NONE
    if marriage_partner_name_of_dd != "":
        return TEXT_STYLE_LT
    return TEXT_STYLE_NONE


class SelectableDropDown(ft.Dropdown):
    def __init__(
        self,
        value: str | None = None,
        options: List[Option] | None = None,
        alignment: ft.Alignment | None = None,
        autofocus: bool | None = None,
        hint_content: ft.Control | None = None,
        icon_content: ft.Control | None = None,
        elevation: int | float | None = None,
        item_height: int | float | None = None,
        max_menu_height: int | float | None = None,
        icon_size: int | float | None = None,
        enable_feedback: bool | None = None,
        padding: int | float | ft.Padding | None = None,
        icon_enabled_color: str | None = None,
        icon_disabled_color: str | None = None,
        on_change: Callable[[ControlEvent], None] | None = None,
        on_focus: Callable[[ControlEvent], None] | None = None,
        on_blur: Callable[[ControlEvent], None] | None = None,
        on_click: Callable[[ControlEvent], None] | None = None,
        text_size: int | float | None = None,
        text_style: ft.TextStyle | None = None,
        label: str | None = None,
        label_style: ft.TextStyle | None = None,
        icon: str | None = None,
        border: ft.InputBorder | None = None,
        color: str | None = None,
        bgcolor: str | None = None,
        border_radius: int | float | ft.BorderRadius | None = None,
        border_width: int | float | None = None,
        border_color: str | None = None,
        focused_color: str | None = None,
        focused_bgcolor: str | None = None,
        focused_border_width: int | float | None = None,
        focused_border_color: str | None = None,
        content_padding: int | float | ft.Padding | None = None,
        dense: bool | None = None,
        filled: bool | None = None,
        fill_color: str | None = None,
        hint_text: str | None = None,
        hint_style: ft.TextStyle | None = None,
        helper_text: str | None = None,
        helper_style: ft.TextStyle | None = None,
        counter_text: str | None = None,
        counter_style: ft.TextStyle | None = None,
        error_text: str | None = None,
        error_style: ft.TextStyle | None = None,
        prefix: ft.Control | None = None,
        prefix_icon: str | None = None,
        prefix_text: str | None = None,
        prefix_style: ft.TextStyle | None = None,
        suffix: ft.Control | None = None,
        suffix_icon: str | None = None,
        suffix_text: str | None = None,
        suffix_style: ft.TextStyle | None = None,
        ref: ft.Ref | None = None,
        key: str | None = None,
        width: int | float | None = None,
        height: int | float | None = None,
        expand: None | bool | int = None,
        expand_loose: bool | None = None,
        col: Dict[str, int | float] | int | float | None = None,
        opacity: int | float | None = None,
        rotate: int | float | ft.Rotate | None = None,
        scale: int | float | ft.Scale | None = None,
        offset: ft.Offset | Tuple[float | int, float | int] | None = None,
        aspect_ratio: int | float | None = None,
        animate_opacity: bool | int | ft.Animation | None = None,
        animate_size: bool | int | ft.Animation | None = None,
        animate_position: bool | int | ft.Animation | None = None,
        animate_rotation: bool | int | ft.Animation | None = None,
        animate_scale: bool | int | ft.Animation | None = None,
        animate_offset: bool | int | ft.Animation | None = None,
        on_animation_end: Callable[[ControlEvent], None] | None = None,
        tooltip: str | None = None,
        visible: bool | None = None,
        disabled: bool | None = None,
        data: Any = None,
    ):
        super().__init__(
            value,
            options,
            alignment,
            autofocus,
            hint_content,
            icon_content,
            elevation,
            item_height,
            max_menu_height,
            icon_size,
            enable_feedback,
            padding,
            icon_enabled_color,
            icon_disabled_color,
            on_change,
            on_focus,
            on_blur,
            on_click,
            text_size,
            text_style,
            label,
            label_style,
            icon,
            border,
            color,
            bgcolor,
            border_radius,
            border_width,
            border_color,
            focused_color,
            focused_bgcolor,
            focused_border_width,
            focused_border_color,
            content_padding,
            dense,
            filled,
            fill_color,
            hint_text,
            hint_style,
            helper_text,
            helper_style,
            counter_text,
            counter_style,
            error_text,
            error_style,
            prefix,
            prefix_icon,
            prefix_text,
            prefix_style,
            suffix,
            suffix_icon,
            suffix_text,
            suffix_style,
            ref,
            key,
            width,
            height,
            expand,
            expand_loose,
            col,
            opacity,
            rotate,
            scale,
            offset,
            aspect_ratio,
            animate_opacity,
            animate_size,
            animate_position,
            animate_rotation,
            animate_scale,
            animate_offset,
            on_animation_end,
            tooltip,
            visible,
            disabled,
            data,
        )
        self.options: list[IndexDropDownOption]

    def set_value_by_index(self, index: int) -> None:
        self.value = self.options[index].text


class IndexDropDownOption(ft.dropdown.Option):
    def __init__(
        self,
        index: int,
        parent_index: int,
        key: str | None = None,
        text: str | None = None,
        content: ft.Control | None = None,
        alignment: ft.Alignment | None = None,
        text_style: ft.TextStyle | None = None,
        on_click: Callable[[ControlEvent], None] | None = None,
        ref=None,
        disabled: bool | None = None,
        visible: bool | None = None,
        data: Any = None,
    ):
        super().__init__(
            key,
            text,
            content,
            alignment,
            text_style,
            on_click,
            ref,
            disabled,
            visible,
            data,
        )
        self.index = index
        self.parent_index = parent_index


class PairRow(ft.Row):
    def __init__(self, character: ch.Character, images_dir: str):
        super().__init__(col={"lg": 6, "xl": 4})
        self.controls = [
            ft.Row(
                controls=[
                    ft.Image(
                        src=os.path.join(images_dir, f"{character.DATA.NAME}.png")
                    ),
                    ft.Text(value=character.DATA.NAME),
                ],
                expand=True,
                expand_loose=True,
            ),
        ]
        self.visible = character.state.exist


class PairColumnParts(NamedTuple):
    row: ft.Row
    dropdown: SelectableDropDown
    dd_options: list[IndexDropDownOption]


def get_pair_column_parts(
    ct: ch.UniqueCharactersTuple,
    on_click_dropdown_option: OptionalEventCallable[Any],
    images_dir: str,
) -> list[PairColumnParts]:
    return_val: list[PairColumnParts] = []
    for i, c in enumerate(ct):
        dd_options = [
            IndexDropDownOption(
                index=0,
                parent_index=i,
                text="ソロエンド" if c.DATA.HAVE_SOLO_END else "エンド無し",
                on_click=on_click_dropdown_option,
            )
        ]
        for p_i, p_name in enumerate(c.DATA.PAIRABLE_NAMES):
            dd_options.append(
                IndexDropDownOption(
                    index=p_i + 1,
                    parent_index=i,
                    # ここでエラーが起きる可能性がある。
                    visible=ct.get_character_by_name(p_name).state.exist,
                    text=get_dropdown_text(
                        pair_name=p_name,
                        is_already_married=p_name in c.state.names_of_married_partner,
                    ),
                    on_click=on_click_dropdown_option,
                )
            )
        dropdown = SelectableDropDown()
        dropdown.expand = True
        dropdown.options = dd_options
        dropdown.bgcolor = ft.colors.SURFACE_CONTAINER_HIGHEST
        dropdown.width = 220
        dropdown.options_fill_horizontally = True
        dropdown.set_value_by_index(0)
        row = PairRow(character=c, images_dir=images_dir)
        row.alignment = ft.MainAxisAlignment.SPACE_BETWEEN
        row.controls.append(dropdown)
        return_val.append(PairColumnParts(row, dropdown, dd_options))
    return return_val
