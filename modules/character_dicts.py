# coding: utf-8
from typing import TypedDict, Any
from typing import TypeGuard


class IsDefaultAndJoinable(TypedDict):
    default: bool
    joinable: bool


class RouteData(TypedDict):
    紅花: IsDefaultAndJoinable
    銀雪: IsDefaultAndJoinable
    蒼月: IsDefaultAndJoinable
    翠風: IsDefaultAndJoinable


class DataDict(TypedDict):
    have_solo_end: bool
    pairable_names: list[str]
    route_data: RouteData


class CharacterDataDict(TypedDict):
    key: str
    value: DataDict


class StateDict(TypedDict):
    exist: bool
    names_of_married_partner: list[str]


class CharacterStateDict(TypedDict):
    key: str
    value: StateDict


def is_route_data(d: dict[Any, Any]) -> TypeGuard[RouteData]:
    route_names = {"紅花", "銀雪", "蒼月", "翠風"}
    keys = {"default", "joinable"}
    if type(d) is not dict:  # type: ignore
        return False
    if len(d.keys()) != len(route_names):
        return False
    if d.keys() != route_names:
        return False
    for v in d.values():
        if type(v) is not dict:
            return False
        if v.keys() != keys:
            return False
        if any([type(v[k]) is not bool for k in keys]):  # type: ignore
            return False
    return True


def is_state_dict(d: dict[Any, Any]) -> TypeGuard[StateDict]:
    keys = {"exist", "names_of_married_partner"}
    if type(d) is not dict:  # type: ignore
        return False
    if d.keys() != keys:
        return False
    exist: bool = d["exist"]
    nmp: list[str] = d["names_of_married_partner"]
    if type(exist) is not bool:
        return False
    if type(nmp) is not list:
        return False
    if any([type(s) is not str for s in nmp]):
        return False
    return True
