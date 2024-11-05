# coding: utf-8
from __future__ import annotations
from .character_dicts import RouteData, is_route_data
from .errors import IncorrectCharacterNameException, IncorrectPairException


def _check_type(v, class_name: type):
    if type(v) is not class_name:
        raise TypeError(f'Expected type is "{class_name}" but received "{type(v)}".')


class CharacterData:
    def __init__(
        self,
        NAME: str,
        HAVE_SOLO_END: bool,
        PAIRABLE_NAMES: list[str],
        ROUTE_DATA: RouteData,
    ) -> None:
        _check_type(NAME, str)
        _check_type(HAVE_SOLO_END, bool)
        _check_type(PAIRABLE_NAMES, list)
        if len(PAIRABLE_NAMES) != len(set(PAIRABLE_NAMES)):
            raise IncorrectPairException(
                f'"{NAME}"の PAIRABLE_NAMES に重複が見つかりました。\n{PAIRABLE_NAMES}'
            )
        if any([type(x) is not str for x in PAIRABLE_NAMES]):
            raise TypeError(PAIRABLE_NAMES)
        if not is_route_data(ROUTE_DATA):
            raise TypeError(ROUTE_DATA)
        self.NAME = NAME
        self.HAVE_SOLO_END = HAVE_SOLO_END
        self.ROUTE_DATA = ROUTE_DATA
        self.PAIRABLE_NAMES = PAIRABLE_NAMES


# names_of_married_partner = []（デフォルト値）として生成すると、キャラクター全体でこのオブジェクトのidが同じになってしまう現象が起きた。
# 一つのnames_of_married_partnerにappendすると、それが全てのキャラクターに反映されてしまった。
class CharacterStateForSaving:
    def __init__(self, exist: bool, names_of_married_partner: list[str]) -> None:
        _check_type(exist, bool)
        _check_type(names_of_married_partner, list)
        self.exist = exist
        self.names_of_married_partner = names_of_married_partner


class Character:
    def __init__(self, DATA: CharacterData) -> None:
        self.DATA = DATA
        self.index: int
        self.state = CharacterStateForSaving(exist=False, names_of_married_partner=[])
        self.__tentative_pair: Character | None = None

    @property
    def tentative_pair(self):
        return self.__tentative_pair

    @tentative_pair.setter
    def tentative_pair(self, v: Character | None):
        if isinstance(v, Character):
            if self.tentative_pair is v:
                raise ValueError(
                    f'"{self.DATA.NAME}"と"{v.DATA.NAME}"は、既に仮ペアです。'
                )
            # 仮結婚
            if v.DATA.NAME in self.DATA.PAIRABLE_NAMES:
                self.__tentative_pair = v
            else:
                raise IncorrectPairException(
                    f'"{self.DATA.NAME}"と{v.DATA.NAME}"は、ペアラブルではありません。'
                )
        else:
            # 離婚
            if isinstance(self.__tentative_pair, Character):
                # self.__tentative_pair.tentative_pair = None
                self.__tentative_pair = None
            else:
                raise IncorrectPairException(
                    f'"{self.DATA.NAME}"が、未婚状態で離婚しようとしています。'
                )


class UniqueCharactersTuple(tuple[Character, ...]):
    def __new__(cls, characters: tuple[Character, ...]):
        if any([type(character) is not Character for character in characters]):
            raise TypeError
        self = tuple.__new__(cls, characters)
        return self

    def __init__(self, characters: tuple[Character, ...]) -> None:
        super().__init__()
        self.__name_to_index_dict: dict[str, int] = {}
        self.__tentative_married_table: list[str] = []
        for i, c in enumerate(self):
            c.index = i
            self.__tentative_married_table.append("")
            self.__name_to_index_dict[c.DATA.NAME] = i

        if len(self) != len(set([c.DATA.NAME for c in self])):
            raise IncorrectCharacterNameException(
                f"名前が重複するキャラクターが存在します。\n{self.__name_to_index_dict=}"
            )

        self.__sort_all_pairables()
        self.__check_all_pairable_are_symmetry()

    def __check_all_pairable_are_symmetry(self):
        for c in self:
            for p_name in c.DATA.PAIRABLE_NAMES:
                p_index = self.__name_to_index_dict[p_name]
                self.check_pair_is_valid(c.index, p_index)

    def __sort_all_pairables(self) -> None:
        for c in self:
            try:
                # キャラクター名と一致しないペアがいる場合、keyErrorが起こる。
                # 本質的にはペアの名前のValueError。
                c.DATA.PAIRABLE_NAMES.sort(
                    key=lambda pair_name: self.__name_to_index_dict[pair_name]
                )
            except KeyError:
                raise IncorrectCharacterNameException(
                    f'"{c.DATA.NAME}"のPAIRABLE_NAMESに、存在しないキャラクター名が含まれています。\n{c.DATA.PAIRABLE_NAMES=}'
                )

    def is_character_name(self, s: str) -> bool:
        return s in self.__name_to_index_dict.keys()

    def get_character_by_name(self, s: str) -> Character:
        if self.is_character_name(s):
            return self[self.__name_to_index_dict[s]]
        else:
            raise IncorrectCharacterNameException(s)

    def get_characters_to_solo_end(self):
        return [
            c
            for c in self
            if all([c.DATA.HAVE_SOLO_END, c.state.exist, c.tentative_pair is None])
        ]

    def get_established_pairs(self):
        _: list[tuple[Character, Character]] = []
        for i, c in enumerate(self):
            tp = c.tentative_pair
            if tp is None:
                continue
            if tp.index > i:
                _.append((c, tp))
        return _

    def ends_to_str(self) -> str:
        solo_end_names = [c.DATA.NAME for c in self.get_characters_to_solo_end()]
        ep = self.get_established_pairs()
        ep_to_str = "\n".join([f"{x[0].DATA.NAME} & {x[1].DATA.NAME}" for x in ep])
        solo_end_to_str = ", ".join(solo_end_names)
        return f"・ペアエンド\n{ep_to_str}\n\n・ソロエンド\n{solo_end_to_str}"

    def check_pair_is_valid(self, index0: int, index1: int):
        if (index0 >= len(self)) or (index1 >= len(self)):
            raise IndexError("タプルの範囲外の不正なインデックスが渡されました。")
        if index0 == index1:
            raise ValueError(
                f"ペアとして、2つの同じindex:{index0}が渡されました。\n{self[index0].DATA.NAME=}"
            )
        if (self[index1].DATA.NAME not in self[index0].DATA.PAIRABLE_NAMES) or (
            self[index0].DATA.NAME not in self[index1].DATA.PAIRABLE_NAMES
        ):
            raise IncorrectPairException(
                f'"{self[index0].DATA.NAME}"と"{self[index1].DATA.NAME}"は正しいペアではありません。'
            )
        return True
