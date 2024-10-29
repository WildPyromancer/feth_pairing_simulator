# coding: utf-8

from typing import Any, Callable

from flet_core.control_event import ControlEvent
import flet as ft
from flet_core.types import OptionalControlEventCallable


class WindowCloseDialog(ft.CupertinoAlertDialog):
    def __init__(
        self,
        open: bool = False,
        modal: bool = True,
        title: ft.Control = ft.Text(value="致命的なエラーの発生"),
        content: ft.Control | None = None,
        ref: ft.Ref | None = None,
        disabled: bool | None = None,
        visible: bool | None = None,
        data: Any = None,
    ):
        super().__init__(
            open=open,
            modal=modal,
            title=title,
            content=content,
            ref=ref,
            disabled=disabled,
            visible=visible,
            data=data,
        )
        self.on_dismiss = self.__close_window
        self.actions = [
            ft.CupertinoDialogAction(text="終了", on_click=self.__close_window),
        ]

    def __close_window(self, e: ControlEvent):
        e.page.close(self)  # type: ignore
        e.page.window.close()  # type: ignore
        exit(False)


class ActionNo(ft.CupertinoDialogAction):
    def __init__(self):
        super().__init__(text="No", on_click=self._handle_click)

    def _handle_click(self, e: ft.ControlEvent):
        self.page.close(self.parent)  # type: ignore


class NavigationBarIconContent(ft.Container):
    def __init__(self, icon_name: str, text: str, text_size: int):
        super().__init__()
        self.margin = 5
        self.content = ft.Column(
            spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(name=icon_name),
                ft.Text(value=text, size=text_size),
            ],
        )
