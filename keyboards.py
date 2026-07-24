from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from locales import get_text

def get_main_keyboard(lang: str, is_paired: bool) -> ReplyKeyboardMarkup:
    if is_paired:
        kb = [
            [KeyboardButton(text=get_text(lang, 'btn_ready'))],
            [KeyboardButton(text=get_text(lang, 'btn_add_topic')), KeyboardButton(text=get_text(lang, 'btn_my_topics'))],
            [KeyboardButton(text=get_text(lang, 'btn_history')), KeyboardButton(text=get_text(lang, 'btn_settings'))]
        ]
    else:
        kb = [
            [KeyboardButton(text=get_text(lang, 'btn_connect'))],
            [KeyboardButton(text=get_text(lang, 'btn_settings'))]
        ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_settings_keyboard(lang: str) -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton(text=get_text(lang, 'btn_lang'), callback_data="change_lang")],
        [InlineKeyboardButton(text=get_text(lang, 'btn_break'), callback_data="break_pair_request")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_lang_keyboard() -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_lang_ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="set_lang_en")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_pair_request_keyboard(req_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Принять", callback_data=f"accept_pair:{req_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_pair:{req_id}")
        ]
    ])

def get_ready_keyboard(req_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Я тоже готов(а)", callback_data=f"confirm_ready:{req_id}")]
    ])

def get_discussion_msg_keyboard(msg_id: int, lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=get_text(lang, 'btn_keep'), callback_data=f"disc_keep:{msg_id}"),
            InlineKeyboardButton(text=get_text(lang, 'btn_resolved'), callback_data=f"disc_res:{msg_id}")
        ]
    ])