# coding: utf-8

from . import sys_path_append  # noqa: F401

import modules.character as ch  # noqa: E402
import modules.character_dicts as cd  # noqa: E402

valid_default_and_joinable = cd.IsDefaultAndJoinable(default=True, joinable=False)

valid_route_data = cd.RouteData(
    紅花=valid_default_and_joinable,
    銀雪=valid_default_and_joinable,
    蒼月=valid_default_and_joinable,
    翠風=valid_default_and_joinable,
)

valid_state_dict = ch.CharacterStateForSaving(
    exist=True, names_of_married_partner=["1"]
)

valid_character_data = ch.CharacterData(
    NAME="0",
    HAVE_SOLO_END=False,
    PAIRABLE_NAMES=["1", "2"],
    ROUTE_DATA=valid_route_data,
)


valid_character0 = ch.Character(DATA=valid_character_data)
