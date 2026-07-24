TEXTS = {
    'ru': {
        'choose_lang': "Пожалуйста, выберите язык / Please select a language:",
        'welcome': "👋 Добро пожаловать! Бот — это ваш безопасный буфер для обсуждения любых тем без ссор.\n\nВаш код для подключения пары: `{code}`\n\nОтправьте этот код или ссылку-приглашение вашему партнёру:\n`https://t.me/{bot_username}?start={code}`",
        'btn_ready': "🚀 Мы готовы",
        'btn_add_topic': "➕ Добавить тему",
        'btn_my_topics': "📝 Мои темы",
        'btn_history': "📜 История обговоренного",
        'btn_settings': "⚙️ Настройки",
        'btn_connect': "🔗 Подключить пару",
        'btn_lang': "🌐 Язык / Language",
        'btn_break': "💔 Разорвать связь",
        'enter_code_prompt': "Отправьте код партнёра в чат или перейдите по его ссылке.",
        'connect_confirm_sender': "У вас уже есть пара. Вы уверены, что хотите разорвать её и отправить новый запрос?",
        'connect_confirm_target': "Пользователь {name} хочет связать с вами профили.",
        'connect_confirm_target_break': "Пользователь {name} хочет связать с вами профили. Это разорвёт вашу текущую связь!",
        'connect_success': "🎉 Вы успешно связали профили! Теперь вы можете сохранять важные темы и обсуждать их вместе.",
        'pair_broken': "💔 Связь была расторгнута. Все неразобранные темы вернулись авторам.",
        'break_warning': "⚠️ Это действие отправит ваши необсужденные сообщения вам же. Другой пользователь их больше не увидит. Разорвать связь?",
        'timeout_pairing_target': "⏱ Пользователь пытался связаться с вами, но время ожидания (2 минуты) вышло.",
        'timeout_pairing_sender': "⏱ Пользователь не ответил на запрос в течение 2 минут.",
        'add_topic_prompt': "Отправьте сообщение (текст, фото, голосовое и т.д.), которое вы хотите обсудить в будущем.",
        'topic_added': "✅ Тема сохранена в ваш список!",
        'no_topics': "У вас пока нет сохранённых тем.",
        'ready_waiting': "⌛ Вы подтвердили готовность! Ожидаем ответа партнёра (у него 1 минута)...",
        'ready_notify_partner': "🔔 **{name} готов(а) обсудить накопленные темы!**\nУ вас есть **1 минута**, чтобы подтвердить готовность.",
        'ready_timeout_sender': "⏱ Время ожидания вышло. Партнёр не успел подтвердить готовность.",
        'ready_timeout_partner': "⏱ Время на подтверждение готовности вышло.",
        'session_start': "🎉 Оба партнёра готовы! Начинаем разбор накопленных тем.",
        'btn_keep': "📌 Оставить",
        'btn_resolved': "✅ Обговорено",
        'marked_resolved': "✅ Отмечено как обговорено",
        'marked_kept': "📌 Оставлено на следующий раз",
    },
    'en': {
        'choose_lang': "Please select a language / Пожалуйста, выберите язык:",
        'welcome': "👋 Welcome! This bot is your safe buffer to discuss sensitive topics calmly.\n\nYour pairing code: `{code}`\n\nShare this code or link with your partner:\n`https://t.me/{bot_username}?start={code}`",
        'btn_ready': "🚀 We're Ready",
        'btn_add_topic': "➕ Add Topic",
        'btn_my_topics': "📝 My Topics",
        'btn_history': "📜 Discussed History",
        'btn_settings': "⚙️ Settings",
        'btn_connect': "🔗 Connect Partner",
        'btn_lang': "🌐 Language / Язык",
        'btn_break': "💔 Break Connection",
        'enter_code_prompt': "Send your partner's code to the chat or click their link.",
        'connect_confirm_sender': "You already have an active connection. Are you sure you want to break it and connect with someone else?",
        'connect_confirm_target': "User {name} wants to pair with you.",
        'connect_confirm_target_break': "User {name} wants to pair with you. Accepting will break your current connection!",
        'connect_success': "🎉 Profiles successfully paired! You can now store and discuss important topics together.",
        'pair_broken': "💔 Connection was broken. Unresolved topics have been returned to their authors.",
        'break_warning': "⚠️ Breaking the connection will send your unresolved messages back to you. The partner won't see them. Break connection?",
        'timeout_pairing_target': "⏱ A connection request was made, but the 2-minute time limit expired.",
        'timeout_pairing_sender': "⏱ Partner did not respond within 2 minutes.",
        'add_topic_prompt': "Send any message (text, photo, voice, etc.) you'd like to discuss later.",
        'topic_added': "✅ Topic saved to your list!",
        'no_topics': "You have no saved topics yet.",
        'ready_waiting': "⌛ You are ready! Waiting for your partner to confirm (1 minute timer)...",
        'ready_notify_partner': "🔔 **{name} is ready to discuss accumulated topics!**\nYou have **1 minute** to confirm.",
        'ready_timeout_sender': "⏱ Time expired. Partner did not confirm in time.",
        'ready_timeout_partner': "⏱ Time limit for confirmation expired.",
        'session_start': "🎉 Both partners are ready! Starting topic review.",
        'btn_keep': "📌 Keep",
        'btn_resolved': "✅ Discussed",
        'marked_resolved': "✅ Marked as discussed",
        'marked_kept': "📌 Kept for next time",
    }
}

def get_text(lang: str, key: str, **kwargs):
    lang_dict = TEXTS.get(lang, TEXTS['ru'])
    text = lang_dict.get(key, TEXTS['ru'].get(key, ""))
    return text.format(**kwargs) if kwargs else text

def get_available_languages():
    return list(TEXTS.keys())

# returns all texts for every language for a given key, like ["Спасибо", "Thank you"] for key 'thank_you'
def get_all_texts(key: str):
    return [TEXTS[lang].get(key, "") for lang in get_available_languages()]