import asyncio
import uuid
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import database as db
from locales import get_text, get_all_texts
from keyboards import get_main_keyboard, get_pair_request_keyboard, get_settings_keyboard

router = Router()
pending_requests = {}

async def process_pairing_code(message: Message, sender: dict, code: str):
    lang = sender['lang']
    target = await db.get_user_by_code(code)

    if not target or target['user_id'] == sender['user_id']:
        await message.answer("❌ Неверный код или это ваш собственный код.")
        return

    req_id = str(uuid.uuid4())[:8]
    pending_requests[req_id] = {
        'sender_id': sender['user_id'],
        'target_id': target['user_id'],
        'active': True
    }

    # Отправляем уведомление целевому пользователю
    target_lang = target['lang']
    msg_key = 'connect_confirm_target_break' if target['pairing_id'] else 'connect_confirm_target'
    text = get_text(target_lang, msg_key, name=sender['name'] or "Пользователь")

    try:
        sent_msg = await message.bot.send_message(
            target['user_id'],
            text,
            reply_markup=get_pair_request_keyboard(req_id)
        )
        await message.answer("📨 Запрос отправлен. Ожидаем ответа (2 минуты)...")
    except Exception:
        await message.answer("❌ Не удалось отправить запрос пользователю.")
        return

    # Запускаем 2-минутный таймер
    await asyncio.sleep(120)
    req = pending_requests.get(req_id)
    if req and req['active']:
        req['active'] = False
        try:
            await sent_msg.edit_text(get_text(target_lang, 'timeout_pairing_target'))
        except Exception:
            pass
        await message.bot.send_message(sender['user_id'], get_text(lang, 'timeout_pairing_sender'))

@router.callback_query(F.data.startswith("accept_pair:"))
async def cb_accept_pair(callback: CallbackQuery):
    req_id = callback.data.split(":")[1]
    req = pending_requests.get(req_id)

    if not req or not req['active']:
        await callback.answer("Время ожидания запроса истекло.", show_alert=True)
        return

    req['active'] = False
    sender_id = req['sender_id']
    target_id = req['target_id']

    # Устанавливаем связь в базе
    await db.set_pair(sender_id, target_id)

    sender = await db.get_user(sender_id)
    target = await db.get_user(target_id)

    await callback.message.edit_text(get_text(target['lang'], 'connect_success'))
    await callback.bot.send_message(
        sender_id,
        get_text(sender['lang'], 'connect_success'),
        reply_markup=get_main_keyboard(sender['lang'], True)
    )
    await callback.message.answer("Меню обновлено", reply_markup=get_main_keyboard(target['lang'], True))

@router.callback_query(F.data.startswith("reject_pair:"))
async def cb_reject_pair(callback: CallbackQuery):
    req_id = callback.data.split(":")[1]
    req = pending_requests.get(req_id)
    if req:
        req['active'] = False
    await callback.message.edit_text("Запрос отклонен.")

@router.callback_query(F.data == "break_pair_request")
async def cb_break_request(callback: CallbackQuery):
    user = await db.get_user(callback.from_user.id)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💔 Да, разорвать", callback_data="confirm_break_pair")],
        [InlineKeyboardButton(text="Отмена", callback_data="cancel_break")]
    ])
    await callback.message.edit_text(get_text(user['lang'], 'break_warning'), reply_markup=kb)

@router.callback_query(F.data == "confirm_break_pair")
async def cb_confirm_break(callback: CallbackQuery):
    user = await db.get_user(callback.from_user.id)
    partner_id = await db.break_pair(user['user_id'])

    await callback.message.edit_text(get_text(user['lang'], 'pair_broken'))
    await callback.message.answer("Главное меню", reply_markup=get_main_keyboard(user['lang'], False))

    if partner_id:
        partner = await db.get_user(partner_id)
        if partner:
            await callback.bot.send_message(
                partner_id,
                get_text(partner['lang'], 'pair_broken'),
                reply_markup=get_main_keyboard(partner['lang'], False)
            )

@router.message(F.text.in_(get_all_texts('btn_connect')))
async def msg_connect_btn(message: Message):
    user = await db.get_user(message.from_user.id)
    await message.answer(get_text(user['lang'], 'enter_code_prompt'))