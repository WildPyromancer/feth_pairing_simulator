# coding: utf-8
from enum import Enum, unique
from typing import TypedDict


@unique
class RouteNames(Enum):
    CRIMSON_FLOWER = "紅花"
    SILVER_SNOW = "銀雪"
    AZURE_MOON = "蒼月"
    VERDANT_WIND = "翠風"


class RouteStatus(TypedDict):
    default: bool
    joinable: bool


class CharactersRouteData(TypedDict):
    紅花: RouteStatus
    銀雪: RouteStatus
    蒼月: RouteStatus
    翠風: RouteStatus


route_color_dict = {
    v[0].value: v[1] for v in zip(RouteNames, ["RED", "GREY", "BLUE", "GREEN"])
}
