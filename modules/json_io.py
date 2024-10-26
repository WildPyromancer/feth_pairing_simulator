# coding: utf-8

import json

from pathlib import Path

from .character import (
    UniqueCharactersTuple,
    CharacterData,
    Character,
)


def json_to_characters_tuple(path: Path) -> UniqueCharactersTuple:
    with open(path, "rt", encoding="utf-8") as file:
        text = json.load(file)
    return UniqueCharactersTuple(
        tuple(
            Character(
                DATA=CharacterData(
                    NAME=data["key"],
                    HAVE_SOLO_END=data["value"]["have_solo_end"],
                    PAIRABLE_NAMES=data["value"]["pairable_names"],
                    ROUTE_DATA=data["value"]["route_data"],
                )
            )
            for data in text
        )
    )
