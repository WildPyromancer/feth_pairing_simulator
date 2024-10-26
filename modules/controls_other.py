# coding: utf-8

from typing import Any, Callable

from flet_core.control_event import ControlEvent
import flet as ft
from flet_core.types import OptionalControlEventCallable


# Obtain consent in the dialog and execute the function.


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
            ft.CupertinoDialogAction(text="終了", on_click=self.__close_window)
        ]

    def __close_window(self, e: ControlEvent):
        e.page.window.close()
        exit(False)

    #    page.overlay.append(dialog)
    #     dialog.open = True


class ActionNo(ft.CupertinoDialogAction):
    def __init__(self):
        super().__init__(text="No", on_click=self._handle_click)

    def _handle_click(self, e: ft.ControlEvent):
        self.parent.open = False
        self.page.update()


# ft.NavigationBarDestination のlabelの文字サイズの変更方法が分からなかったため、自作。
class NavigationBarIconContent(ft.Column):
    def __init__(self, icon_name: str, text: str, text_size: int):
        super().__init__()
        self.spacing = 0
        self.controls = [
            ft.Row(
                spacing=0,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[ft.Icon(name=icon_name)],
            ),
            ft.Row(
                spacing=0,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[ft.Text(value=text, size=text_size)],
            ),
        ]


# class ActionDialogObtainConsentAndExecuteFunction(ft.CupertinoAlertDialog):
#     def __init__(
#         self,
#         func: Callable[[], Any],
#         open: bool = False,
#         modal: bool = False,
#         title: ft.Control = ft.Text("確認"),
#         content: ft.Control | None = None,
#         on_dismiss: OptionalControlEventCallable[Any] = None,
#         ref: ft.Ref | None = None,
#         disabled: bool | None = None,
#         visible: bool | None = None,
#         data: Any = None,
#     ):
#         super().__init__(
#             open=open,
#             modal=modal,
#             title=title,
#             content=content,
#             on_dismiss=on_dismiss,
#             ref=ref,
#             disabled=disabled,
#             visible=visible,
#             data=data,
#         )
#         self.func = func
#         self.actions = [
#             ft.CupertinoDialogAction(text="Yes", on_click=self.__handle_click_Yes),
#             ActionNo(),
#         ]

#     def __handle_click_Yes(self, e: ControlEvent):
#         self.open = False
#         e.control.page.update()
#         self.func()
