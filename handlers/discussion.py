import asyncio
import uuid
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
import database as db
from locales import get_text, get_all_texts
from keyboards import get_ready_keyboard, get_discussion_msg_keyboard

router = Router()
ready_sessions = {}

@router.message(F.text.in_(get_all_texts('btn_ready')))
async def cmd_ready(message: Message):
    user = await db.get_user(message.from_user.id)
    if not user or not user['pairing_id']:
        return

    partner = await db.get_user(user['pairing_id'])
    session_id = str(uuid.uuid4())[:8]

    ready_sessions[session_id] = {
        'initiator': user['user_id'],
        'partner': partner['user_id'],
        'active': True
    }

    await message.answer(get_text(user['lang'], 'ready_waiting'))

    try:
        sent_msg = await message.bot.send_message(
            partner['user_id'],
            get_text(partner['lang'], 'ready_notify_partner', name=user['name'] or "Партнёр"),
            reply_markup=get_ready_keyboard(session_id),
            parse_mode="Markdown"
        )
    except Exception:
        return

    # 1-минутный таймер
    await asyncio.sleep(60)
    sess = ready_sessions.get(session_id)
    if sess and sess['active']:
        sess['active'] = False
        await message.answer(get_text(user['lang'], 'ready_timeout_sender'))
        try:
            await sent_msg.edit_text(get_text(partner['lang'], 'ready_timeout_partner'))
        except Exception:
            pass

@router.callback_query(F.data.startswith("confirm_ready:"))
async def cb_confirm_ready(callback: CallbackQuery):
    session_id = callback.data.split(":")[1]
    sess = ready_sessions.get(session_id)

    if not sess or not sess['active']:
        await callback.answer("Время ожидания вышло.", show_alert=True)
        return

    sess['active'] = False
    u1_id = sess['initiator']
    u2_id = sess['partner']

    u1 = await db.get_user(u1_id)
    u2 = await db.get_user(u2_id)

    await callback.message.edit_text("✅ Взаимная готовность подтверждена!")
    await callback.bot.send_message(u1_id, get_text(u1['lang'], 'session_start'))
    await callback.bot.send_message(u2_id, get_text(u2['lang'], 'session_start'))

    # Отправляем накапливавшиеся сообщения перекрёстно
    msgs_u1 = await db.get_messages_for_pair(u1_id, u2_id) # Написал u1 для u2
    msgs_u2 = await db.get_messages_for_pair(u2_id, u1_id) # Написал u2 для u1

    # Доставляем u1 сообщения от u2
    for m in msgs_u2:
        await send_discussion_item(callback.bot, u1_id, m, u1['lang'])

    # Доставляем u2 сообщения от u1
    for m in msgs_u1:
        await send_discussion_item(callback.bot, u2_id, m, u2['lang'])

async def send_discussion_item(bot: Bot, chat_id: int, msg, lang: str):
    kb = get_discussion_msg_keyboard(msg['id'], lang)
    if msg['media_type'] == 'text':
        await bot.send_message(chat_id, f"💭 {msg['text']}", reply_markup=kb, disable_notification=True)
    elif msg['media_type'] == 'photo':
        await bot.send_photo(chat_id, msg['file_id'], caption=msg['caption'], reply_markup=kb, disable_notification=True)
    elif msg['media_type'] == 'voice':
        await bot.send_voice(chat_id, msg['file_id'], caption=msg['caption'], reply_markup=kb, disable_notification=True)
    elif msg['media_type'] == 'video':
        await bot.send_video(chat_id, msg['file_id'], caption=msg['caption'], reply_markup=kb, disable_notification=True)

@router.callback_query(F.data.startswith("disc_res:"))
async def cb_disc_resolved(callback: CallbackQuery):
    msg_id = int(callback.data.split(":")[1])
    await db.mark_message_resolved(msg_id)
    user = await db.get_user(callback.from_user.id)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.reply(get_text(user['lang'], 'marked_resolved'))

@router.callback_query(F.data.startswith("disc_keep:"))
async def cb_disc_keep(callback: CallbackQuery):
    user = await db.get_user(callback.from_user.id)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.reply(get_text(user['lang'], 'marked_kept'))

@router.message(F.text.in_(get_all_texts('btn_history')))
async def cmd_history(message: Message):
    user = await db.get_user(message.from_user.id)
    if not user or not user['pairing_id']:
        return

    history = await db.get_resolved_history(user['user_id'], user['pairing_id'])
    if not history:
        await message.answer("История пуста.")
        return

    await message.answer("📜 **Последние 20 обговоренных тем:**", parse_mode="Markdown")
    for item in history:
        text = item['text'] or item['caption'] or f"[{item['media_type']}]"
        await message.answer(f"✅ {text}", disable_notification=True)