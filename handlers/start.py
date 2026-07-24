from aiogram import Router, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, CallbackQuery
import database as db
from locales import get_text
from keyboards import get_lang_keyboard, get_main_keyboard
from handlers.pairing import process_pairing_code

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject):
    user = await db.get_user(message.from_user.id)
    args = command.args

    if not user:
        # Новый пользователь
        await message.answer(get_text('ru', 'choose_lang'), reply_markup=get_lang_keyboard())
        # Запоминаем диплинк если был
        if args:
            # Можем временно обработать код после выбора языка
            pass
        return

    bot_info = await message.bot.get_me()
    text = get_text(user['lang'], 'welcome', code=user['pairing_code'], bot_username=bot_info.username)
    await message.answer(text, parse_mode="Markdown", reply_markup=get_main_keyboard(user['lang'], bool(user['pairing_id'])))

    # Если передан диплинк код
    if args and not user['pairing_id']:
        await process_pairing_code(message, user, args)

@router.callback_query(F.data.startswith("set_lang_"))
async def cb_set_lang(callback: CallbackQuery):
    lang = callback.data.split("_")[2]
    user = await db.get_user(callback.from_user.id)

    if not user:
        user = await db.create_user(callback.from_user.id, callback.from_user.first_name, lang)
    else:
        await db.update_user_lang(callback.from_user.id, lang)

    bot_info = await callback.bot.get_me()
    text = get_text(lang, 'welcome', code=user['pairing_code'], bot_username=bot_info.username)
    
    await callback.message.delete()
    await callback.message.answer(text, parse_mode="Markdown", reply_markup=get_main_keyboard(lang, bool(user['pairing_id'])))