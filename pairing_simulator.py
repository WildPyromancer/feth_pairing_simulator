# coding: utf-8

from pathlib import Path
from logging import config, getLogger
from time import sleep

import flet as ft  # type: ignore

from modules.routes import RouteNames, route_color_dict
import modules.character as ch
import modules.errors as er
import modules.controls_of_character_selection as ccs
import modules.controls_other as co
import modules.logging_conf
import modules.controls_of_pair_selection as cps
import modules.json_io as ji
import modules.character_dicts as cd
import modules.my_theme as th


# 方針
#
# 使うライブラリの数を減らす。出力ファイルの起動時間やサイズを無駄に肥大化させない。

# 注意
#
# コントロール周りのindexは、ミスが起こりやすい場所。
# 分かりやすい変数名を設定する。

# to do
#
# route to colors

# bugs
#


async def main(page: ft.Page):
    #
    # 変数宣言
    #

    config.dictConfig(modules.logging_conf.LOGGING_CONFIG)
    logger = getLogger(__name__)

    PARENT_PATH = Path(__file__).resolve().parent
    # 最初に読み込まれる、必須のデータファイル。
    # キャラクターデータ、ペア履歴も内包する。
    PATH_OF_CHARACTER_DATA_JSON = PARENT_PATH.joinpath(
        "./data/character_data.json"
    ).resolve()

    # asserts下のディレクトリは、ルート（/）直下に配置される。
    images_dir = "/images"
    # pyinstallerによるパッケージ化用。
    # images_dir = str(PARENT_PATH.joinpath("./images").resolve())
    character_face_dir = images_dir + "/character_face"

    ct: ch.UniqueCharactersTuple
    route_only_pair = [
        ({"ベレト", "レア"}, "銀雪"),
        ({"ベレス", "レア"}, "銀雪"),
        ({"メルセデス", "アロイス"}, "銀雪, 蒼月, 翠風"),
        ({"イングリット", "セテス"}, "蒼月"),
    ]

    app_title = "風花雪月ペアシミュレーター"
    page.title = app_title

    # demo動画撮影用
    # page.window.width = 720
    # page.window.height = 720

    mts = th.MyTextStyle()

    confirmation_title = ft.Text(
        value="確認", style=th.MyTextStyle(size=th.TextSize.large.value)
    )

    theme = th.MyTheme()
    page.theme = theme
    #
    # 関数宣言
    #

    def open_window_close_dialog(body: str):
        """ダイアログでユーザーに通知し、終了ボタンクリックかダイアログ終了時にwindowを閉じる関数。
        即座に処理を止めるわけではない。そうしたい場合は直後にreturn等で返す必要がある。
        """
        d = co.WindowCloseDialog(content=ft.Text(value=body, style=mts))
        page.open(d)

    def open_dialog(body: str, title: str | None = None, selectable: bool = False):
        d = ft.CupertinoAlertDialog(
            title=ft.Text(value=title, style=mts),
            content=ft.Text(value=body, style=mts, selectable=selectable),
        )
        page.open(d)

    async def update_ct_state_with_client_storage(
        ct: ch.UniqueCharactersTuple,
    ) -> None:
        """引数 ct の全ての要素の state を更新する破壊的関数。"""
        clst = page.client_storage
        keys = await clst.get_keys_async("")
        for k in keys:
            if not ct.is_character_name(k):
                await clst.remove_async(k)
                logger.warning(
                    f"キャラクター名ではないkey、「{k}」がクライアントストレージに保存されていたので削除しました。"
                )
                continue
            value = await clst.get_async(k)
            if not cd.is_state_dict(value):  # type: ignore
                await clst.remove_async(k)
                logger.warning(
                    f"不正な値のkey「{k=}」がクライアントストレージに保存されていたので削除しました。"
                )
                continue
            c = ct.get_character_by_name(k)
            c.state.names_of_married_partner = value["names_of_married_partner"]  # type: ignore
            c.state.exist = value["exist"]  # type: ignore

    # それぞれのキャラクターが持つルートデータに応じて存在を変更する関数。
    # 任意のRoutesを渡すコントロールによって行われる。

    def synchronize_existence_and_controls(c: ch.Character) -> None:
        """characterのstate.existに基づいて、コントロールの変更をする関数。"""
        logger.debug(f'{"+" if c.state.exist else "-"} {c.DATA.NAME}')
        column_parts_of_character_selection[c.index].checkbox.value = c.state.exist
        column_parts_of_pair_selection[c.index].row.visible = c.state.exist
        # 変更されて、trueになった。
        if c.state.exist:
            column_parts_of_character_selection[c.index].image.color = None
        # 変更されて、 falseになった。
        else:
            column_parts_of_character_selection[
                c.index
            ].image.color = ccs.IMAGE_BLEND_COLOR
            # 結婚していたら離婚させる。
            tp = c.tentative_pair
            if isinstance(tp, ch.Character):
                divorce_and_update_controls(c, tp)

        # キャラクターのペアラブルの行のドロップダウンリストを修正する。
        try:
            for p_name in c.DATA.PAIRABLE_NAMES:
                pair_character = ct.get_character_by_name(p_name)
                options_index = 1 + pair_character.DATA.PAIRABLE_NAMES.index(
                    c.DATA.NAME
                )
                column_parts_of_pair_selection[pair_character.index].dd_options[
                    options_index
                ].visible = c.state.exist
        except er.IncorrectCharacterNameException as ex:
            logger.error(ex)
            open_window_close_dialog(
                er.ErrorCodeAndUserMessage.INCORRECT_CHARACTER_NAME.value
            )
            return

    def divorce_and_update_controls(c_row: ch.Character, c_dd: ch.Character) -> None:
        def set_a_dd_value_to_default(c: ch.Character) -> None:
            update_text_style_of_dd_options(c)
            column_parts_of_pair_selection[c.index].dropdown.set_value_by_index(0)

        logger.debug(
            f"[divorce_and_update_controls]{c_row.DATA.NAME} and {c_dd.DATA.NAME}"
        )
        try:
            c_row.tentative_pair = None
            c_dd.tentative_pair = None
        except er.IncorrectPairException as ex:
            logger.error(ex)
            open_window_close_dialog(er.ErrorCodeAndUserMessage.INCORRECT_PAIR.value)
            return
        set_a_dd_value_to_default(c_dd)
        set_a_dd_value_to_default(c_row)

    def tentative_pairing_and_update_controls(
        c_row: ch.Character, c_dd: ch.Character
    ) -> None:
        # ペアにペアがいたら、離婚させる。
        def divorce_if_fiance_has_a_marriage_partner(c: ch.Character):
            if isinstance(c.tentative_pair, ch.Character):
                divorce_and_update_controls(c, c.tentative_pair)

        logger.debug(
            f"[tentative_pairing_and_update_controls]{c_row.DATA.NAME} and {c_dd.DATA.NAME}"
        )
        # 場合によっては、ここで結婚選択者のddの値がデフォルトになってしまう。
        divorce_if_fiance_has_a_marriage_partner(c_row)
        divorce_if_fiance_has_a_marriage_partner(c_dd)
        # なので元の値に戻しておく。
        _dd_options_index = 1 + c_row.DATA.PAIRABLE_NAMES.index(c_dd.DATA.NAME)
        column_parts_of_pair_selection[c_row.index].dropdown.set_value_by_index(
            _dd_options_index
        )
        _dd_options_index = 1 + c_dd.DATA.PAIRABLE_NAMES.index(c_row.DATA.NAME)
        column_parts_of_pair_selection[c_dd.index].dropdown.set_value_by_index(
            _dd_options_index
        )
        try:
            c_row.tentative_pair = c_dd
            c_dd.tentative_pair = c_row
        except er.IncorrectPairException as ex:
            logger.error(ex)
            open_window_close_dialog(er.ErrorCodeAndUserMessage.INCORRECT_PAIR.value)
            return
        update_text_style_of_dd_options(c_row)
        update_text_style_of_dd_options(c_dd)
        for x in route_only_pair:
            if {c_dd.DATA.NAME, c_row.DATA.NAME} == x[0]:
                open_dialog(
                    body=f"{c_dd.DATA.NAME}と{c_row.DATA.NAME}は、{x[1]}ルート限定のペアです。",
                    title="注意",
                )
                return

    def update_text_style_of_dd_options(c: ch.Character) -> None:
        for pair_index, pairable_name in enumerate(c.DATA.PAIRABLE_NAMES):
            try:
                pair_character = ct.get_character_by_name(pairable_name)
                # default_value が先頭にあるので+1。
                # ペアのペアリスト（dd）内での自身の位置。
                options_index = 1 + pair_character.DATA.PAIRABLE_NAMES.index(
                    c.DATA.NAME
                )
                dd_opt = column_parts_of_pair_selection[
                    pair_character.index
                ].dd_options[options_index]
                tp = c.tentative_pair
                dd_opt.text_style = cps.get_a_textstyle(
                    character_name_of_row=pairable_name,
                    marriage_partner_name_of_dd=tp.DATA.NAME
                    if isinstance(tp, ch.Character)
                    else "",
                )
                k = ["{", "}"]
                logger.debug(
                    f'{k[0]}text_style={"LT  " if dd_opt.text_style == cps.TEXT_STYLE_LT else "None"}, "{dd_opt.text}"{k[1]} -> {pairable_name}[{pair_index}]'
                )
            except er.IncorrectCharacterNameException as ex:
                logger.error(ex)
                open_window_close_dialog(
                    er.ErrorCodeAndUserMessage.INCORRECT_CHARACTER_NAME.value
                )
                return

    # ペアの状態によって、ドロップダウンオプションのテキストスタイルをラインスルーにしたりNoneに戻したりする関数。
    # ミスが起きやすいので注意。
    # 実際に操作するのはcのペアのrow.dd

    def handle_checkbox_is_changed(e: ft.ControlEvent) -> None:
        logger.info("ControlEvent: handle_checkbox_is_changed")
        if not isinstance(e, ft.ControlEvent):  # type: ignore
            open_window_close_dialog(
                er.ErrorCodeAndUserMessage.UNEXPECTED_CONTROL_EVENT.value
            )
            logger.error(f"{e=}はコントロールイベントではありません。")
            return
        if not isinstance(e.control, ft.Checkbox):  # type: ignore
            logger.error(
                f"{er.ErrorCodeAndUserMessage.UNEXPECTED_CONTROL_EVENT.name} with {e.control}"  # type: ignore
            )
            open_window_close_dialog(
                er.ErrorCodeAndUserMessage.UNEXPECTED_CONTROL_EVENT.value
            )
            return
        if e.control.label is None:
            logger.error(
                f"{er.ErrorCodeAndUserMessage.INCORRECT_CONTROL.name} with labelless {e.control}"
            )
            open_window_close_dialog(er.ErrorCodeAndUserMessage.INCORRECT_CONTROL.value)
            return
        if type(e.control.value) is not bool:
            logger.error(f"{er.ErrorCodeAndUserMessage.INCORRECT_CONTROL.name}")
            open_window_close_dialog(
                f"{er.ErrorCodeAndUserMessage.INCORRECT_CONTROL.value}"
            )
            return
        try:
            c = ct.get_character_by_name(e.control.label)
            c.state.exist = e.control.value
            synchronize_existence_and_controls(c)
        except er.IncorrectCharacterNameException as ex:
            logger.error(ex)
            open_window_close_dialog(
                er.ErrorCodeAndUserMessage.INCORRECT_CHARACTER_NAME.value
            )
            return
        page.update(main_content)  # type: ignore

    def handle_dropdown_option_click(e: ft.ControlEvent) -> None:
        logger.info("ControlEvent: handle_dropdown_option_click")
        if not isinstance(e, ft.ControlEvent):  # type: ignore
            open_window_close_dialog(
                er.ErrorCodeAndUserMessage.UNEXPECTED_CONTROL_EVENT.value
            )
            logger.error(f"{e=}はコントロールイベントではありません。")
            return
        if not isinstance(e.control, cps.IndexDropDownOption):  # type: ignore
            logger.error(
                f"{er.ErrorCodeAndUserMessage.UNEXPECTED_CONTROL_EVENT} with {e.control}"  # type: ignore
            )
            open_window_close_dialog(
                er.ErrorCodeAndUserMessage.UNEXPECTED_CONTROL_EVENT.value
            )
            return
        index_of_row = e.control.parent_index
        index_of_dropdown = e.control.index
        # ドロップダウンの先頭はペアではないため。
        index_in_pairable = index_of_dropdown - 1
        if index_of_row > len(ct):
            logger.error(
                f"{er.ErrorCodeAndUserMessage.INCONSISTENCY_BETWEEN_VARIABLE_AND_CONTROL.name} with {index_of_row}, キャラクター数と行数に違いがあります。"
            )
            open_window_close_dialog(
                er.ErrorCodeAndUserMessage.INCONSISTENCY_BETWEEN_VARIABLE_AND_CONTROL.value
            )
            return
        row_character = ct[index_of_row]
        if index_of_dropdown > len(row_character.DATA.PAIRABLE_NAMES):
            logger.error(
                f"{er.ErrorCodeAndUserMessage.INCONSISTENCY_BETWEEN_VARIABLE_AND_CONTROL.name} with {row_character.DATA.NAME}, ペア数とドロップダウンオプション数に違いがあります。"
            )
            open_window_close_dialog(
                er.ErrorCodeAndUserMessage.INCONSISTENCY_BETWEEN_VARIABLE_AND_CONTROL.value
            )
            return

        # default_valueが選択された場合。
        if index_of_dropdown == 0:
            if row_character.tentative_pair is None:
                return
            divorce_and_update_controls(row_character, row_character.tentative_pair)
        else:
            try:
                dd_character = ct.get_character_by_name(
                    row_character.DATA.PAIRABLE_NAMES[index_in_pairable]
                )
                if row_character.tentative_pair == dd_character:
                    # 同じ相手と既婚なら何もしない
                    return
                # 結婚処理
                tentative_pairing_and_update_controls(row_character, dd_character)
            except er.IncorrectCharacterNameException as ex:
                logger.error(ex)
                open_window_close_dialog(
                    er.ErrorCodeAndUserMessage.INCORRECT_CHARACTER_NAME.value
                )

        page.update(main_content)  # type: ignore

    # メニューバー 履歴
    async def handle_save_button_click(e: ft.ControlEvent) -> None:
        async def _save_state_to_client_storage(e: ft.ControlEvent) -> None:
            for c in ct:
                tp = c.tentative_pair
                if tp is None:
                    await page.client_storage.set_async(c.DATA.NAME, c.state.__dict__)
                    continue
                if tp.DATA.NAME in c.state.names_of_married_partner:
                    await page.client_storage.set_async(c.DATA.NAME, c.state.__dict__)
                    continue
                # 結婚が確定したペアのドロップダウンを、未 → 既 に更新。
                c.state.names_of_married_partner.append(tp.DATA.NAME)
                target_column = column_parts_of_pair_selection[c.index]
                dd_opt_index = 1 + c.DATA.PAIRABLE_NAMES.index(tp.DATA.NAME)
                target_column.dd_options[dd_opt_index].text = cps.get_dropdown_text(
                    tp.DATA.NAME, True
                )
                target_column.dropdown.set_value_by_index(dd_opt_index)
                await page.client_storage.set_async(c.DATA.NAME, c.state.__dict__)
            page.close(dialog)
            page.update(main_content)  # type: ignore

        logger.info("ControlEvent: handle_save_button_click")
        dialog = ft.CupertinoAlertDialog(
            content=ft.Text(
                value="現在の所属キャラクター選択の内容を保存し、成立しているペアをペア履歴に追加します。\nなお、これらのデータはユーザーのストレージに保存されます。\nよろしいですか？",
                style=mts,
            ),
            title=confirmation_title,
            actions=[
                ft.CupertinoDialogAction(
                    text="Yes",
                    on_click=_save_state_to_client_storage,
                ),
                co.ActionNo(),
            ],
        )
        page.open(dialog)

    async def handle_remove_pair_button_click(e: ft.ControlEvent):
        async def _process_one_by_one(pair: tuple[ch.Character, ch.Character]):
            # 操作対象はpair[0]
            if pair[1].DATA.NAME not in pair[0].state.names_of_married_partner:
                return
            pair[0].state.names_of_married_partner.remove(pair[1].DATA.NAME)
            target_column = column_parts_of_pair_selection[pair[0].index]
            dd_opt_index = 1 + pair[0].DATA.PAIRABLE_NAMES.index(pair[1].DATA.NAME)
            target_column.dd_options[dd_opt_index].text = cps.get_dropdown_text(
                pair[1].DATA.NAME, False
            )
            target_column.dropdown.set_value_by_index(dd_opt_index)
            old_hist = await page.client_storage.get_async(pair[0].DATA.NAME)
            if not cd.is_state_dict(old_hist):
                await page.client_storage.set_async(
                    pair[0].DATA.NAME, pair[0].state.__dict__
                )
                logger.warning(
                    f"クライアントストレージの'{pair[0].DATA.NAME}'に、不正な値「{old_hist}」が保存されていたので更新しました。"
                )
                return
            assert type(old_hist) is dict
            old_hist["names_of_married_partner"] = pair[
                0
            ].state.names_of_married_partner
            await page.client_storage.set_async(pair[0].DATA.NAME, old_hist)

        async def _remove_mp_from_client_storage(e: ft.ControlEvent) -> None:
            logger.info("_remove_mp_from_client_storage")
            for pair in ct.get_established_pairs():
                await _process_one_by_one(pair)
                await _process_one_by_one((pair[1], pair[0]))
            page.close(dialog)
            page.update(main_content)  # type: ignore

        logger.info("ControlEvent: handle_remove_pair_button_click")
        dialog = co.ft.CupertinoAlertDialog(
            content=ft.Text(
                value="現在成立している全てのペアをペア履歴から削除します。\nよろしいですか？",
                style=mts,
            ),
            title=confirmation_title,
            actions=[
                ft.CupertinoDialogAction(
                    text="Yes", on_click=_remove_mp_from_client_storage
                ),
                co.ActionNo(),
            ],
        )
        page.open(dialog)

    async def handle_delete_all_history_button_click(e: ft.ControlEvent):
        async def _clear_all_history(e: ft.ControlEvent):
            page.close(second_dialog)
            await page.client_storage.clear_async()

        def _two_step_approval(e: ft.ControlEvent):
            page.close(first_dialog)
            sleep(0.5)
            page.open(second_dialog)

        logger.info("ControlEvent: handle_delete_all_history_button_click")
        if not isinstance(e, ft.ControlEvent):  # type: ignore
            open_window_close_dialog(
                er.ErrorCodeAndUserMessage.UNEXPECTED_CONTROL_EVENT.value
            )
            logger.error(f"{e=}はコントロールイベントではありません。")
            return
        first_dialog = ft.CupertinoAlertDialog(
            content=ft.Text(
                value="このアプリケーションが「セーブ」ボタンによってストレージに作成した全てのデータを削除します。\nよろしいですか？",
                style=mts,
            ),
            open=True,
            title=confirmation_title,
            actions=[
                ft.CupertinoDialogAction(text="Yes", on_click=_two_step_approval),
                co.ActionNo(),
            ],
        )
        second_dialog = ft.CupertinoAlertDialog(
            title=ft.Text(
                value="最後の確認",
                style=ft.TextStyle(size=th.TextSize.large.value, color="red"),
            ),
            content=ft.Text(
                value="本当に削除しますか？",
                style=mts,
            ),
            actions=[
                ft.CupertinoDialogAction(text="Yes", on_click=_clear_all_history),
                co.ActionNo(),
            ],
        )
        page.open(first_dialog)

    async def handle_load_state_from_client_storage_button_click(
        e: ft.ControlEvent,
    ) -> None:
        """引数 ct の全ての要素の state を更新する破壊的関数。"""
        logger.info("ControlEvent: handle_load_state_from_client_storage_button_click")
        clst = page.client_storage
        keys = await clst.get_keys_async("")
        for k in keys:
            if not ct.is_character_name(k):
                await clst.remove_async(k)
                continue
            value = await clst.get_async(k)
            if not cd.is_state_dict(value):  # type: ignore
                await clst.remove_async(k)
                continue
            c = ct.get_character_by_name(k)
            if c.state.exist != value["exist"]:  # type: ignore
                c.state.exist = not c.state.exist
                synchronize_existence_and_controls(c)
        page.update(main_content)  # type: ignore

    # メニューバー 操作

    def handle_load_existence_from_route_preset_button_click(
        e: ft.ControlEvent,
    ) -> None:
        logger.info(
            "ControlEvent: handle_load_existence_from_route_preset_button_click"
        )
        if not isinstance(e, ft.ControlEvent):  # type: ignore
            open_window_close_dialog(
                er.ErrorCodeAndUserMessage.UNEXPECTED_CONTROL_EVENT.value
            )
            logger.error(f"{e=}はコントロールイベントではありません。")
            return
        if isinstance(e.control.data, RouteNames):  # type: ignore
            selected_route = e.control.data.value  # type: ignore
        else:
            logger.error(er.ErrorCodeAndUserMessage.UNEXPECTED_CONTROL_EVENT.name)
            open_window_close_dialog(
                er.ErrorCodeAndUserMessage.UNEXPECTED_CONTROL_EVENT.value
            )
            return
        logger.debug(f"Load route of {selected_route}.")
        for c in ct:
            d = c.DATA.ROUTE_DATA[selected_route]
            change_flag = False
            if d["default"] and (not c.state.exist):
                change_flag = True
            if (not d["joinable"]) and c.state.exist:
                change_flag = True
            if change_flag:
                c.state.exist = not c.state.exist
                synchronize_existence_and_controls(c)

        theme.color_scheme_seed = route_color_dict[selected_route]
        page.update(main_content)  # type: ignore

    def handle_character_selection_clear_button_click(e: ft.ControlEvent) -> None:
        logger.info("ControlEvent: handle_character_selection_clear_button_click")
        for c in ct:
            if not c.state.exist:
                continue
            c.state.exist = False
            synchronize_existence_and_controls(c)
        page.update(main_content)  # type: ignore

    def handle_make_all_pairs_divorced_button_click(e: ft.ControlEvent) -> None:
        logger.info("ControlEvent: handle_make_all_pairs_divorced_button_click")
        for c in ct:
            if isinstance(c.tentative_pair, ch.Character):
                divorce_and_update_controls(c, c.tentative_pair)
        page.update(main_content)  # type: ignore

    # メニューバー その他
    def handle_display_ending_text_button_click(e: ft.ControlEvent) -> None:
        logger.info("ControlEvent: handle_display_ending_text_button_click")
        open_dialog(body=ct.endings_to_str(), selectable=True, title="組み合わせ一覧")

    def handle_display_achievement_rate(e: ft.ControlEvent) -> None:
        total = int(0.5 * sum([len(c.DATA.PAIRABLE_NAMES) for c in ct]))
        current = int(0.5 * sum([len(c.state.names_of_married_partner) for c in ct]))
        open_dialog(
            body=f"{current} / {total} = {100*current/total:.1f} %",
            title="ペアエンド達成率",
            selectable=True,
        )

    # メニューバー ヘルプ
    def handle_how_to_use_button_click(e: ft.ControlEvent):
        def return_view(e: ft.ControlEvent):
            page.views.pop()
            page.update()  # type: ignore

        return_button = ft.Container(
            on_click=return_view,
            content=ft.Row(
                controls=[
                    ft.Icon(name=ft.icons.ARROW_BACK_OUTLINED),
                    ft.Text(
                        value="戻る",
                        style=th.MyTextStyle(size=th.TextSize.large.value),
                        weight=ft.FontWeight.BOLD,
                    ),
                ]
            ),
        )

        usage_md_path = "./docs/usage.md"
        try:
            file = open(file=usage_md_path, mode="rt", encoding="utf-8")
            md_text = file.read()
        except Exception as ex:
            open_dialog(
                body=f"ファイル「{usage_md_path}」の読み込みに失敗しました",
                title="エラーの発生",
            )
            logger.warning(ex)
            return

        md = ft.Markdown(value=str(md_text), expand=True)
        htu_view = ft.View(
            controls=[
                return_button,
                ft.Column(controls=[md], expand=True, scroll=ft.ScrollMode.ALWAYS),
            ],
        )
        page.views.append(htu_view)
        page.update()  # type: ignore

    #
    # 処理の開始
    #

    logger.info(f"Processing is start in {PARENT_PATH}")

    # 辞書の読み込みとCharactersTupleの構築。
    if not PATH_OF_CHARACTER_DATA_JSON.is_file():
        logger.critical(
            f"{er.ErrorCodeAndUserMessage.DATA_FILE_DOES_NOT_EXIST.name} with {PATH_OF_CHARACTER_DATA_JSON}"
        )
        open_window_close_dialog(
            er.ErrorCodeAndUserMessage.DATA_FILE_DOES_NOT_EXIST.value
        )
        return

    try:
        ct = ji.json_to_characters_tuple(PATH_OF_CHARACTER_DATA_JSON)
    except Exception as ex:
        logger.error(ex)
        open_window_close_dialog(
            er.ErrorCodeAndUserMessage.FAILED_TO_LOAD_DATA_DICTIONARY.value
        )
        return

    await update_ct_state_with_client_storage(ct)

    # コントロールの作成。

    # 所属タブの内容の作成。

    # bgcolorの他にもう一個設定しないとバグる。
    menu_style = ft.MenuStyle(
        bgcolor=ft.colors.OUTLINE_VARIANT,
        alignment=ft.alignment.top_left,
    )
    sub_menu_style = ft.MenuStyle(
        bgcolor=ft.colors.SURFACE_CONTAINER_HIGHEST,
        alignment=ft.alignment.bottom_left,
    )

    menubar = ft.MenuBar(
        expand=True,
        style=menu_style,
        controls=[
            ft.SubmenuButton(
                width=th.TextSize.medium.value * 5,
                content=ft.Text("履歴", style=mts, text_align=ft.TextAlign.CENTER),
                menu_style=sub_menu_style,
                controls=[
                    ft.MenuItemButton(
                        content=ft.Text("セーブ", style=mts),
                        on_click=handle_save_button_click,
                    ),
                    ft.MenuItemButton(
                        content=ft.Text("ロード", style=mts),
                        on_click=handle_load_state_from_client_storage_button_click,
                    ),
                    ft.MenuItemButton(
                        content=ft.Text("ペアを履歴から削除", style=mts),
                        on_click=handle_remove_pair_button_click,
                    ),
                    ft.MenuItemButton(
                        content=ft.Text("全ての履歴を削除", style=mts),
                        on_click=handle_delete_all_history_button_click,
                    ),
                ],
            ),
            ft.SubmenuButton(
                width=th.TextSize.medium.value * 5,
                content=ft.Text("操作", style=mts, text_align=ft.TextAlign.CENTER),
                menu_style=sub_menu_style,
                controls=[
                    ft.SubmenuButton(
                        content=ft.Text("ルートプリセットで自動選択", style=mts),
                        controls=[
                            ft.MenuItemButton(
                                style=ft.ButtonStyle(
                                    bgcolor=f"{route_color_dict[r.value]}"
                                ),
                                content=ft.Text(r.value, size=th.TextSize.medium.value),
                                data=r,
                                on_click=handle_load_existence_from_route_preset_button_click,
                            )
                            for r in RouteNames
                        ],
                    ),
                    ft.MenuItemButton(
                        content=ft.Text("選択のクリア", style=mts),
                        on_click=handle_character_selection_clear_button_click,
                    ),
                    ft.MenuItemButton(
                        content=ft.Text("全てのペアを解消", style=mts),
                        on_click=handle_make_all_pairs_divorced_button_click,
                    ),
                ],
            ),
            ft.SubmenuButton(
                width=th.TextSize.medium.value * 6,
                content=ft.Text("その他", style=mts, text_align=ft.TextAlign.CENTER),
                menu_style=sub_menu_style,
                controls=[
                    ft.MenuItemButton(
                        content=ft.Text("組み合わせのまとめ", style=mts),
                        on_click=handle_display_ending_text_button_click,
                    ),
                    ft.MenuItemButton(
                        content=ft.Text("達成率", style=mts),
                        on_click=handle_display_achievement_rate,
                    ),
                ],
            ),
            ft.SubmenuButton(
                width=th.TextSize.medium.value * 6,
                content=ft.Text("ヘルプ", style=mts, text_align=ft.TextAlign.CENTER),
                menu_style=sub_menu_style,
                controls=[
                    ft.MenuItemButton(
                        content=ft.Text("使い方", style=mts),
                        on_click=handle_how_to_use_button_click,
                    ),
                    ft.MenuItemButton(
                        content=ft.Image(
                            src=f"{images_dir}/github-mark-white.svg",
                            width=32,
                            height=32,
                        ),
                        on_click=lambda e: page.launch_url(
                            url="https://github.com/WildPyromancer/feth_pairing_simulator"
                        ),
                    ),
                ],
            ),
        ],
    )

    column_parts_of_character_selection = ccs.get_existence_column_parts(
        ct, handle_checkbox_is_changed, character_face_dir
    )

    column_of_character_selection = ft.Column(
        expand=True,
        scroll=ft.ScrollMode.ALWAYS,
        controls=[
            ft.ResponsiveRow(
                controls=[x.row for x in column_parts_of_character_selection],
            )
        ],
    )

    # ペアタブの内容の作成。

    column_parts_of_pair_selection = cps.get_pair_column_parts(
        ct, handle_dropdown_option_click, character_face_dir
    )

    column_of_pair_selection = ft.Column(
        expand=True,
        scroll=ft.ScrollMode.ALWAYS,
        controls=[
            ft.ResponsiveRow(
                controls=[x.row for x in column_parts_of_pair_selection],
            )
        ],
    )

    main_content = ft.Container(content=column_of_character_selection, expand=True)

    def handle_navigation_bar_change(e: ft.ControlEvent):
        if e.control.selected_index == 0:
            main_content.content = column_of_character_selection
        elif e.control.selected_index == 1:
            main_content.content = column_of_pair_selection
        else:
            return
        page.update(main_content)  # type: ignore

    page.navigation_bar = ft.CupertinoNavigationBar(
        bgcolor=ft.colors.ON_INVERSE_SURFACE,
        on_change=handle_navigation_bar_change,
        height=60,
        destinations=[
            ft.NavigationBarDestination(
                icon_content=co.NavigationBarIconContent(
                    ft.icons.MANAGE_ACCOUNTS,
                    "所属キャラクター選択",
                    th.TextSize.small.value,
                )
            ),
            ft.NavigationBarDestination(
                icon_content=co.NavigationBarIconContent(
                    ft.icons.FAVORITE, "ペア選択", th.TextSize.small.value
                )
            ),
        ],
    )
    page.add(ft.Row(controls=[menubar], expand=False), main_content)

    # def theme_changed(e):
    #     page.theme_mode = (
    #         ft.ThemeMode.DARK
    #         if page.theme_mode == ft.ThemeMode.LIGHT
    #         else ft.ThemeMode.LIGHT
    #     )
    #     page.update()

    # page.add(ft.Switch(on_change=theme_changed))

    logger.info("The start-up process was successful.")


if __name__ == "__main__":
    ft.app(target=main)  # type: ignore
