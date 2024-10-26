import flet as ft
import json
from typing import Any

_wait_time = 5


async def set(key: str, value: Any, page: ft.Page):
    value = page._convert_attr_json(value)
    await page._invoke_method_async(
        "clientStorage:set",
        {"key": key, "value": value},
        wait_timeout=_wait_time,
    )


async def get(key: str, page: ft.Page):
    result = await page._invoke_method_async(
        method_name="clientStorage:get",
        arguments={"key": key},
        wait_timeout=_wait_time,
        wait_for_result=True,
    )
    if result is None:
        return None
    return json.loads(json.loads(result))


async def remove(key: str, page: ft.Page):
    await page._invoke_method_async(
        method_name="clientStorage:remove",
        arguments={"key": key},
        wait_timeout=_wait_time,
    )


async def clear(page: ft.Page):
    await page._invoke_method_async(
        method_name="clientStorage:clear", wait_timeout=_wait_time
    )


async def get_keys(key: str, page: ft.Page) -> list[str]:
    result = await page._invoke_method_async(
        method_name="clientStorage:getkeys",
        arguments={"key_prefix": key},
        wait_timeout=_wait_time,
        wait_for_result=True,
    )
    return json.loads(result)
