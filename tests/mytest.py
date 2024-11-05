# coding: utf-8
import unittest
import copy

from . import sys_path_append  # noqa: F401

from . import dummy_data as dd

import modules.character as ch  # noqa: E402
import modules.character_dicts as cd  # noqa: E402


class CharacterTest(unittest.TestCase):
    def test_check_type(self):
        result = ch._check_type("a", str)
        self.assertIsNone(result)
        with self.assertRaises(
            TypeError, msg="Expected type is <class 'bool'> but received <class 'int'>."
        ):
            ch._check_type(1, bool)

    def test_character_data(self):
        with self.assertRaises(TypeError):
            ch.CharacterData(
                NAME=0,
                HAVE_SOLO_END=False,
                PAIRABLE_NAMES=["a"],
                ROUTE_DATA=dd.valid_route_data,
            )
        # type HAVE_SOLO_END
        with self.assertRaises(TypeError):
            ch.CharacterData(
                NAME="aaaa",
                HAVE_SOLO_END=0,
                PAIRABLE_NAMES=["a"],
                ROUTE_DATA=dd.valid_route_data,
            )
        # type ROUTE_DATA
        with self.assertRaises(TypeError):
            ch.CharacterData(
                NAME="b", HAVE_SOLO_END=False, PAIRABLE_NAMES=["a"], ROUTE_DATA=None
            )
        with self.assertRaises(TypeError):
            ch.CharacterData(
                NAME="a",
                HAVE_SOLO_END=False,
                PAIRABLE_NAMES=[1],
                ROUTE_DATA=dd.valid_route_data,
            )

        with self.assertRaises(ch.IncorrectPairException):
            ch.CharacterData(
                NAME="a",
                HAVE_SOLO_END=True,
                PAIRABLE_NAMES=["b", "b"],
                ROUTE_DATA=dd.valid_route_data,
            )

    def test_unique_characters_tuple(self):
        # キャラクターの型のテスト
        with self.assertRaises(TypeError):
            ch.UniqueCharactersTuple(characters=(dd.valid_character0, 0))

        # 存在しないペアのテスト
        with self.assertRaises(ch.IncorrectCharacterNameException):
            ch.UniqueCharactersTuple(characters=(dd.valid_character0,))

        # 重複するキャラクター名のテスト
        with self.assertRaises(ch.IncorrectCharacterNameException):
            ch.UniqueCharactersTuple(
                characters=(dd.valid_character0, dd.valid_character0)
            )

        valid_character1 = ch.Character(
            DATA=ch.CharacterData(
                NAME="1",
                HAVE_SOLO_END=False,
                PAIRABLE_NAMES=["0"],
                ROUTE_DATA=dd.valid_route_data,
            )
        )

        valid_character2 = ch.Character(
            DATA=ch.CharacterData(
                NAME="2",
                HAVE_SOLO_END=False,
                PAIRABLE_NAMES=["0"],
                ROUTE_DATA=dd.valid_route_data,
            )
        )

        # 片思いのペア。
        with self.assertRaises(ch.IncorrectPairException):
            ch.UniqueCharactersTuple(
                (
                    dd.valid_character0,
                    valid_character1,
                    valid_character2,
                    ch.Character(
                        DATA=ch.CharacterData(
                            NAME="unrequited_love",
                            HAVE_SOLO_END=False,
                            PAIRABLE_NAMES=["0"],
                            ROUTE_DATA=dd.valid_route_data,
                        )
                    ),
                )
            )

        # ペアラブルに自身の名前があるキャラクター。
        self_pair_character = ch.Character(
            DATA=ch.CharacterData(
                NAME="self_pair",
                HAVE_SOLO_END=False,
                PAIRABLE_NAMES=["self_pair"],
                ROUTE_DATA=dd.valid_route_data,
            )
        )

        with self.assertRaises(ValueError):
            ch.UniqueCharactersTuple(
                (
                    dd.valid_character0,
                    valid_character1,
                    valid_character2,
                    self_pair_character,
                )
            )

        valid_ct = ch.UniqueCharactersTuple(
            (dd.valid_character0, valid_character1, valid_character2)
        )

        # is_character_name()のテスト。
        with self.assertRaises(IndexError):
            valid_ct.check_pair_is_valid(100, 1)
        self.assertEqual(valid_ct.is_character_name("存在しないキャラクター名"), False)
        self.assertEqual(valid_ct.is_character_name("0"), True)

        self.assertIs(type(valid_ct.get_character_by_name("0")), ch.Character)
        with self.assertRaises(ch.IncorrectCharacterNameException):
            valid_ct.get_character_by_name("存在しないキャラクター名")
        # incorrect pair
        with self.assertRaises(ch.IncorrectPairException):
            valid_character1.tentative_pair = valid_character2
        # 未婚離婚
        with self.assertRaises(ch.IncorrectPairException):
            dd.valid_character0.tentative_pair = None
        dd.valid_character0.tentative_pair = valid_character1
        valid_character1.tentative_pair = dd.valid_character0
        # 重婚
        with self.assertRaises(ValueError):
            dd.valid_character0.tentative_pair = valid_character1
        self.assertEqual(dd.valid_character0.tentative_pair, valid_character1)
        self.assertEqual(
            valid_ct.get_established_pairs(), [(dd.valid_character0, valid_character1)]
        )
        self.assertEqual(
            valid_ct.ends_to_str(),
            f"・ペアエンド\n{dd.valid_character0.DATA.NAME} & {valid_character1.DATA.NAME}\n\n・ソロエンド\n",
        )

        valid_character1.tentative_pair = None


class CharacterDictsTest(unittest.TestCase):
    def test_is_route_data(self):
        rd = copy.deepcopy(dd.valid_route_data)
        self.assertEqual(cd.is_route_data(rd), True)
        rd["紅花"]["default"] = 0
        self.assertEqual(cd.is_route_data(rd), False)
        del rd["紅花"]["default"]
        rd["紅花"]["b"] = True
        self.assertEqual(cd.is_route_data(rd), False)
        rd["紅花"] = 0
        self.assertEqual(cd.is_route_data(rd), False)
        del rd["紅花"]
        rd["a"] = 0
        self.assertEqual(cd.is_route_data(rd), False)
        del rd["a"]
        self.assertEqual(cd.is_route_data(rd), False)
        rd = "a"
        self.assertEqual(cd.is_route_data(rd), False)

    def test_is_state_dict(self):
        sd = copy.deepcopy(dd.valid_state_dict)
        self.assertEqual(cd.is_state_dict(sd.__dict__), True)
        sd.names_of_married_partner = [1, "1"]
        self.assertEqual(cd.is_state_dict(sd.__dict__), False)
        sd.names_of_married_partner = True  # type: ignore
        self.assertEqual(cd.is_state_dict(sd.__dict__), False)
        sd.exist = 0  # type: ignore
        self.assertEqual(cd.is_state_dict(sd.__dict__), False)
        del sd.exist
        self.assertEqual(cd.is_state_dict(sd.__dict__), False)
        self.assertEqual(cd.is_state_dict(10), False)
