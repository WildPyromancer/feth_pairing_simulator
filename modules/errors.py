# coding: utf-8
from enum import Enum


class ErrorCodeAndUserMessage(Enum):
    DATA_FILE_DOES_NOT_EXIST = "データファイルが存在しません。"
    FAILED_TO_LOAD_DATA_DICTIONARY = "データファイルの読み込みに失敗しました。"
    INCONSISTENCY_BETWEEN_VARIABLE_AND_CONTROL = (
        "コントロールと変数間で、値の不一致が起きています。"
    )
    INCORRECT_CHARACTER_NAME = "存在しないキャラクターの参照が発生しました。"
    INCORRECT_CONTROL = "コントロールに不備があります。"
    INCORRECT_PAIR = "不正なペアを参照しています。"
    UNEXPECTED_CONTROL_EVENT = "予期しないコントロールイベントが発生しました。"
    UNEXPECTED_ERROR = "予期しないエラーが発生しました。"


class IncorrectCharacterNameException(Exception):
    pass


class IncorrectPairException(Exception):
    pass
