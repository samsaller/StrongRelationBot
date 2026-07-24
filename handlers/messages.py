from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import database as db
from locales import get_text, get_all_texts
from keyboards import get_settings_keyboard, get_lang_keyboard

router = Router()

class EditMessageState(StatesGroup):
    waiting_for_new_text = State()

@router.message(F.text.in_(get_all_texts('btn_add_topic')))
async def cmd_add_topic(message: Message):
    user = await db.get_user(message.from_user.id)
    await message.answer(get_text(user['lang'], 'add_topic_prompt'))

@router.message(F.text.in_(get_all_texts('btn_settings')))
async def cmd_settings(message: Message):
    user = await db.get_user(message.from_user.id)
    await message.answer(get_text(user['lang'], 'btn_settings'), reply_markup=get_settings_keyboard(user['lang']))
    # TODO: fix change_lang callback

@router.message(F.text.in_(get_all_texts('btn_my_topics')))
async def cmd_my_topics(message: Message):
    user = await db.get_user(message.from_user.id)
    topics = await db.get_user_pending_messages(user['user_id'])

    if not topics:
        await message.answer(get_text(user['lang'], 'no_topics'))
        return

    for t in topics:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✏️ Изменить", callback_data=f"edit_msg:{t['id']}"),
             InlineKeyboardButton(text="🗑 Удалить", callback_data=f"del_msg:{t['id']}")]
        ])
        if t['media_type'] == 'text':
            await message.answer(f"📌 {t['text']}", reply_markup=kb)
        elif t['media_type'] == 'photo':
            await message.answer_photo(t['file_id'], caption=t['caption'] or "", reply_markup=kb)
        elif t['media_type'] == 'voice':
            await message.answer_voice(t['file_id'], caption=t['caption'] or "", reply_markup=kb)
        elif t['media_type'] == 'video':
            await message.answer_video(t['file_id'], caption=t['caption'] or "", reply_markup=kb)

@router.callback_query(F.data.startswith("del_msg:"))
async def cb_del_msg(callback: CallbackQuery):
    msg_id = int(callback.data.split(":")[1])
    await db.delete_message(msg_id)
    await callback.message.delete()
    await callback.answer("Удалено.")

@router.callback_query(F.data.startswith("edit_msg:"))
async def cb_edit_msg(callback: CallbackQuery, state: FSMContext):
    msg_id = int(callback.data.split(":")[1])
    await state.update_data(edit_msg_id=msg_id)
    await state.set_state(EditMessageState.waiting_for_new_text)
    await callback.message.answer("Введите новый текст для сообщения:")
    await callback.answer()

@router.message(EditMessageState.waiting_for_new_text)
async def process_new_text(message: Message, state: FSMContext):
    data = await state.get_data()
    msg_id = data.get("edit_msg_id")
    await db.update_message_text(msg_id, message.text, message.text)
    await state.clear()
    await message.answer("✅ Сообщение обновлено!")

# Обработчик сохранения новых сообщений/медиа
@router.message(F.content_type.in_({'text', 'photo', 'voice', 'video', 'document'}))
async def handle_incoming_media(message: Message):
    user = await db.get_user(message.from_user.id)
    if not user or not user['pairing_id']:
        # Если вводят код вручную
        if message.text and len(message.text.strip()) == 8:
            from handlers.pairing import process_pairing_code
            await process_pairing_code(message, user, message.text.strip())
        return

    pair_id = user['pairing_id']
    if message.text:
        await db.add_message(user['user_id'], pair_id, text=message.text, media_type='text')
    elif message.photo:
        await db.add_message(user['user_id'], pair_id, media_type='photo', file_id=message.photo[-1].file_id, caption=message.caption)
    elif message.voice:
        await db.add_message(user['user_id'], pair_id, media_type='voice', file_id=message.voice.file_id, caption=message.caption)
    elif message.video:
        await db.add_message(user['user_id'], pair_id, media_type='video', file_id=message.video.file_id, caption=message.caption)

    await message.answer(get_text(user['lang'], 'topic_added'))