import telebot
from telebot import types
import random

# ==================== НАСТРОЙКИ БОТА ====================
TOKEN_PART1 = "8844824430:"
TOKEN_PART2 = "AAGeeS8GHA89eeQ3gilRWG159ZWgXcFwltQ"
BOT_TOKEN = TOKEN_PART1 + TOKEN_PART2
SUPER_ADMIN_USERNAME = "lytixx"
# ========================================================

bot = telebot.TeleBot(BOT_TOKEN)

admins = {SUPER_ADMIN_USERNAME.lower()}
stats = {}
rp_commands = {
    "обкашлить": "{user1} обкашлил вопросы с {user2} 🤝",
    "трахнуть": "{user1} трахнул {user2} 🔞",
    "обнять": "{user1} крепко обнял {user2} 🤗",
    "поцеловать": "{user1} нежно поцеловал {user2} 😘",
    "кусь": "{user1} сделал кусь {user2} 😼"
}
user_states = {}
LATE_WORDS = ["опоздал", "опоздала", "опоздание", "проспал", "проспала", "задержался", "задержалась"]

SYSTEM_COMMANDS = {"команды", "стата", "топ", "профиль", "баланс", "перевести", "магазин", "купить", "казино", "инвентарь", "+монеты", "баланс-админ", "give", "поставить", "бизнес", "промокод", "клан"}

# ================= ЭКОНОМИКА =================
balances = {}
inventory = {}
equipped = {}
promocodes = {}

# ================= КЛАНЫ =================
clans = {}
user_clan = {}

SHOP_ITEMS = {
    "котик": {"price": 50, "emoji": "🐱", "desc": "Милый котик", "type": "pet"},
    "пёсик": {"price": 50, "emoji": "🐶", "desc": "Верный пёсик", "type": "pet"},
    "дракон": {"price": 150, "emoji": "🐉", "desc": "Огнедышащий дракон", "type": "pet"},
    "единорог": {"price": 200, "emoji": "🦄", "desc": "Волшебный единорог", "type": "pet"},
    "феникс": {"price": 300, "emoji": "🔥", "desc": "Птица-феникс", "type": "pet"},
    "пингвин": {"price": 70, "emoji": "🐧", "desc": "Деловой пингвин", "type": "pet"},
    "робот": {"price": 250, "emoji": "🤖", "desc": "Робот-помощник", "type": "pet"},
    "призрак": {"price": 120, "emoji": "👻", "desc": "Дружелюбный призрак", "type": "pet"},
    "лада": {"price": 1000, "emoji": "🚗", "desc": "Лада Веста", "type": "car"},
    "уазик": {"price": 800, "emoji": "🚙", "desc": "УАЗик (настоящий вездеход)", "type": "car"},
    "мерседес": {"price": 5000, "emoji": "🚘", "desc": "Mercedes-Benz", "type": "car"},
    "ламборгини": {"price": 15000, "emoji": "🏎️", "desc": "Lamborghini", "type": "car"},
    "бугатти": {"price": 30000, "emoji": "🚀", "desc": "Bugatti Chiron", "type": "car"},
    "квартира": {"price": 2000, "emoji": "🏢", "desc": "Уютная квартира", "type": "house"},
    "коттедж": {"price": 10000, "emoji": "🏡", "desc": "Загородный коттедж", "type": "house"},
    "особняк": {"price": 50000, "emoji": "🏰", "desc": "Роскошный особняк", "type": "house"},
}

BUSINESSES = {
    "кб": {"price": 5000, "emoji": "🛒", "desc": "Магазин у дома", "income": 50},
    "пятерочка": {"price": 10000, "emoji": "🏪", "desc": "Пятёрочка", "income": 100},
    "магнит": {"price": 25000, "emoji": "🛍️", "desc": "Магнит", "income": 250},
    "мет": {"price": 50000, "emoji": "🧪", "desc": "Незаконная варка метамфетамина 😈", "income": 500},
}

def get_user_name(user):
    return f"@{user.username}" if user.username else user.first_name

def get_user_rank(count):
    if count >= 1000: return "👑 Легенда чата"
    elif count >= 500: return "🔥 Мега-активист"
    elif count >= 100: return "⭐ Активист"
    elif count >= 50: return "💬 Болтун"
    elif count >= 10: return "👋 Новичок"
    else: return "🌱 Гость"

def get_balance(chat_id, user_id):
    if chat_id not in balances: balances[chat_id] = {}
    if user_id not in balances[chat_id]: balances[chat_id][user_id] = 0
    return balances[chat_id][user_id]

def add_coins(chat_id, user_id, amount):
    if chat_id not in balances: balances[chat_id] = {}
    if user_id not in balances[chat_id]: balances[chat_id][user_id] = 0
    balances[chat_id][user_id] += amount

def format_shop_items(item_type):
    text = ""
    for name, item in SHOP_ITEMS.items():
        if item["type"] == item_type:
            text += f"{item['emoji']} **{name.capitalize()}** — {item['price']} 🪙 ({item['desc']})\n"
    return text

def set_equipped(chat_id, user_id, item_type, item_name):
    if chat_id not in equipped: equipped[chat_id] = {}
    if user_id not in equipped[chat_id]: equipped[chat_id][user_id] = {}
    equipped[chat_id][user_id][item_type] = item_name

# ================= АДМИНКА В ЛС =================

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.type != 'private': return
    username = message.from_user.username
    if username and username.lower() in admins:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row("➕ Назначить админа", "🎭 Добавить РП-команду")
        markup.row("💰 Выдать монеты", "🛒 Купить бизнес")
        bot.send_message(message.chat.id, "Привет, Босс! Доступна админ-панель.", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Привет! Напиши «купить бизнес», чтобы открыть бизнес-меню.", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).row("🛒 Купить бизнес"))

@bot.message_handler(func=lambda msg: msg.chat.type == 'private' and msg.from_user.username and msg.from_user.username.lower() in admins)
def handle_admin_buttons(message):
    if message.text == "➕ Назначить админа":
        bot.send_message(message.chat.id, "Введите username нового админа (без @):")
        user_states[message.chat.id] = "waiting_for_admin_username"
    elif message.text == "🎭 Добавить РП-команду":
        bot.send_message(message.chat.id, "Введите имя команды (например: `ударить`):")
        user_states[message.chat.id] = "waiting_for_rp_name"
    elif message.text == "💰 Выдать монеты":
        bot.send_message(message.chat.id, "Введите в формате: `<ID чата> <ID пользователя> <сумма>`\n\nПример: `-1001234567890 123456789 1000`")
        user_states[message.chat.id] = "waiting_for_coins_admin"
    elif message.text == "🛒 Купить бизнес":
        show_business_menu(message.chat.id, message.from_user.id)

@bot.message_handler(func=lambda msg: msg.chat.type == 'private' and msg.chat.id in user_states)
def process_admin_input(message):
    state = user_states.get(message.chat.id)
    if state == "waiting_for_admin_username":
        new_admin = message.text.strip().replace("@", "").lower()
        admins.add(new_admin)
        bot.send_message(message.chat.id, f"✅ @{new_admin} назначен администратором!")
        del user_states[message.chat.id]
    elif state == "waiting_for_rp_name":
        cmd_name = message.text.strip().lower()
        if cmd_name in SYSTEM_COMMANDS:
            bot.send_message(message.chat.id, "❌ Это имя занято системной командой. Введите другое.")
            return
        user_states[message.chat.id] = f"waiting_for_rp_text:{cmd_name}"
        bot.send_message(message.chat.id, f"Введите текст ответа для `{cmd_name}`.\nТеги: `{{user1}}` и `{{user2}}`")
    elif state.startswith("waiting_for_rp_text:"):
        _, cmd_name = state.split(":", 1)
        rp_commands[cmd_name] = message.text.strip()
        bot.send_message(message.chat.id, f"✅ РП-команда `{cmd_name}` добавлена!")
        del user_states[message.chat.id]
    elif state == "waiting_for_coins_admin":
        parts = message.text.strip().split()
        if len(parts) != 3:
            bot.send_message(message.chat.id, "❌ Формат: `<ID чата> <ID пользователя> <сумма>`")
            return
        try:
            chat_id = int(parts[0])
            target_user_id = int(parts[1])
            amount = int(parts[2])
        except ValueError:
            bot.send_message(message.chat.id, "❌ ID и сумма должны быть числами.")
            return
        add_coins(chat_id, target_user_id, amount)
        bot.send_message(message.chat.id, f"✅ Пользователю `{target_user_id}` в чате `{chat_id}` выдано {amount} 🪙.")
        del user_states[message.chat.id]

# ================= ФУНКЦИЯ МЕНЮ БИЗНЕСОВ (ЛС) =================
def show_business_menu(chat_id, user_id):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for name, item in BUSINESSES.items():
        markup.add(types.InlineKeyboardButton(f"{item['emoji']} {name.capitalize()} — {item['price']} 🪙", callback_data=f"buybiz|{name}|{chat_id}"))
    bot.send_message(chat_id, "🛒 **Выбери бизнес для покупки:**\n(Доход начисляется раз в час при активности в чате)", reply_markup=markup, parse_mode="Markdown")

# ================= ГЛАВНЫЙ ОБРАБОТЧИК ГРУППЫ =================
@bot.message_handler(func=lambda msg: msg.chat.type in ['group', 'supergroup'])
def group_messages_handler(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_name = get_user_name(message.from_user)
    text = message.text.strip() if message.text else ""
    text_lower = text.lower()

    if chat_id not in stats: stats[chat_id] = {}
    if user_id not in stats[chat_id]:
        stats[chat_id][user_id] = {"name": user_name, "count": 0, "late": 0}
    stats[chat_id][user_id]["count"] += 1
    if any(w in text_lower for w in LATE_WORDS):
        stats[chat_id][user_id]["late"] += 1

    add_coins(chat_id, user_id, 1)

    # === /give ===
    if text_lower.startswith("/give") or text_lower.startswith("give "):
        if message.from_user.username and message.from_user.username.lower() == SUPER_ADMIN_USERNAME.lower():
            parts = text.split()
            if parts[0].lower() == "/give":
                if len(parts) < 3:
                    bot.reply_to(message, "❌ Формат: `/give <@username|ID> <сумма>`")
                    return
                target_str, amount = parts[1], int(parts[2])
            else:
                if len(parts) < 3:
                    bot.reply_to(message, "❌ Формат: `give <@username|ID> <сумма>`")
                    return
                target_str, amount = parts[1], int(parts[2])

            if amount <= 0:
                bot.reply_to(message, "❌ Сумма должна быть больше нуля.")
                return

            target_id = None
            target_name = None
            if target_str.startswith("@"):
                uname = target_str[1:].lower()
                for uid, data in stats[chat_id].items():
                    if data["name"].lower() == f"@{uname}":
                        target_id, target_name = uid, data["name"]
                        break
            else:
                try:
                    target_id = int(target_str)
                    target_name = stats[chat_id].get(target_id, {}).get("name", f"ID {target_id}")
                except ValueError:
                    bot.reply_to(message, "❌ Некорректный пользователь.")
                    return

            if target_id is None:
                bot.reply_to(message, "❌ Пользователь не найден в этом чате.")
                return

            add_coins(chat_id, target_id, amount)
            bot.reply_to(message, f"💰 {user_name} выдал **{amount}** 🪙 пользователю {target_name}!", parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ У вас нет прав на эту команду.")
        return

    # === /PROMO ===
    if text_lower.startswith("/promo"):
        if message.from_user.username and message.from_user.username.lower() == SUPER_ADMIN_USERNAME.lower():
            parts = text.split()
            if len(parts) == 1:
                bot.reply_to(message, "❌ Формат: `/promo <код> <тип> <название> <кол-во>`\nТипы: `money`, `car`, `house`, `business`\nПример: `/promo PROMO1 money 5000 1`")
                return
            try:
                code = parts[1]
                ptype = parts[2].lower()
                pname = parts[3].lower() if ptype != "money" else "0"
                count = int(parts[4]) if len(parts) > 4 else 1
                if ptype not in ["money", "car", "house", "business"]:
                    bot.reply_to(message, "❌ Неверный тип. Используйте: money, car, house, business.")
                    return
                promocodes[code.lower()] = {"type": ptype, "name": pname, "count": count}
                bot.reply_to(message, f"✅ Промокод `{code}` создан! Активируйте его в ЛС бота командой `промокод {code}`.", parse_mode="Markdown")
            except Exception:
                bot.reply_to(message, "❌ Ошибка формата. Пример: `/promo PROMO1 money 5000 1`")
        else:
            bot.reply_to(message, "❌ У вас нет прав на эту команду.")
        return

    # === КУПИТЬ БИЗНЕС ===
    if text_lower == "купить бизнес":
        bot.reply_to(message, f"🛒 {user_name}, зайдите в **личные сообщения** бота и напишите там `купить бизнес`, чтобы открыть меню бизнесов!", parse_mode="Markdown")
        return

    # === +МОНЕТЫ ===
    if text_lower.startswith("+монеты "):
        if message.from_user.username and message.from_user.username.lower() == SUPER_ADMIN_USERNAME.lower():
            parts = text.split()
            if len(parts) < 3:
                bot.reply_to(message, "❌ Формат: `+монеты <сумма> <@username>`")
                return
            amount = int(parts[1])
            target_username = parts[2].replace("@", "").lower()
            target_id = target_name = None
            for uid, data in stats[chat_id].items():
                if data["name"].lower() == f"@{target_username}":
                    target_id, target_name = uid, data["name"]
                    break
            if target_id is None:
                bot.reply_to(message, "❌ Пользователь не найден в чате.")
                return
            add_coins(chat_id, target_id, amount)
            bot.reply_to(message, f"💰 {user_name} выдал **{amount}** 🪙 пользователю {target_name}!", parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ У вас нет прав на эту команду.")
        return

    # === БАЛАНС-АДМИН ===
    if text_lower.startswith("баланс-админ"):
        if message.from_user.username and message.from_user.username.lower() == SUPER_ADMIN_USERNAME.lower():
            parts = text.split()
            if len(parts) == 1:
                target = message.reply_to_message.from_user if message.reply_to_message else message.from_user
                bot.reply_to(message, f"💰 Баланс {get_user_name(target)}: **{get_balance(chat_id, target.id)}** 🪙", parse_mode="Markdown")
                return
            elif parts[1].lower() == "все":
                sorted_balances = sorted(balances.get(chat_id, {}).items(), key=lambda x: x[1], reverse=True)
                reply = "💰 **Балансы:**\n\n"
                for uid, coins in sorted_balances:
                    uname = stats[chat_id][uid]["name"] if uid in stats[chat_id] else f"ID {uid}"
                    reply += f"• {uname} — {coins} 🪙\n"
                bot.send_message(chat_id, reply, parse_mode="Markdown")
                return
            else:
                target_username = parts[1].replace("@", "").lower()
                target_id = target_name = None
                for uid, data in stats[chat_id].items():
                    if data["name"].lower() == f"@{target_username}":
                        target_id, target_name = uid, data["name"]
                        break
                if target_id is None:
                    bot.reply_to(message, "❌ Пользователь не найден.")
                    return
                bot.reply_to(message, f"💰 Баланс {target_name}: **{get_balance(chat_id, target_id)}** 🪙", parse_mode="Markdown")
                return
        else:
            bot.reply_to(message, "❌ У вас нет прав на эту команду.")
        return

    # === КЛАНЫ ===
    if text_lower.startswith("клан "):
        parts = text.split()
        if len(parts) < 2:
            bot.reply_to(message, "❌ Формат: `клан создать <название>`, `клан пригласить <@username>`, `клан выйти`, `клан информация`")
            return
        subcmd = parts[1].lower()

        if subcmd == "создать":
            if len(parts) < 3:
                bot.reply_to(message, "❌ Укажите название клана: `клан создать <название>`")
                return
            clan_name = " ".join(parts[2:]).strip()
            if chat_id in user_clan and user_id in user_clan[chat_id]:
                bot.reply_to(message, "❌ Вы уже состоите в клане.")
                return
            if chat_id not in clans: clans[chat_id] = {}
            if clan_name in clans[chat_id]:
                bot.reply_to(message, "❌ Клан с таким названием уже существует.")
                return
            clans[chat_id][clan_name] = {"leader": user_id, "members": [user_id]}
            if chat_id not in user_clan: user_clan[chat_id] = {}
            user_clan[chat_id][user_id] = clan_name
            bot.reply_to(message, f"✅ Клан **{clan_name}** создан! Лидер: {user_name}", parse_mode="Markdown")
            return

        if subcmd == "пригласить":
            if len(parts) < 3:
                bot.reply_to(message, "❌ Укажите пользователя: `клан пригласить @username`")
                return
            if chat_id not in user_clan or user_id not in user_clan[chat_id]:
                bot.reply_to(message, "❌ Вы не состоите в клане.")
                return
            clan_name = user_clan[chat_id][user_id]
            if clans[chat_id][clan_name]["leader"] != user_id:
                bot.reply_to(message, "❌ Только лидер может приглашать.")
                return
            target_username = parts[2].replace("@", "").lower()
            target_id = None
            for uid, data in stats[chat_id].items():
                if data["name"].lower() == f"@{target_username}":
                    target_id = uid
                    break
            if target_id is None:
                bot.reply_to(message, "❌ Пользователь не найден в чате.")
                return
            if chat_id in user_clan and target_id in user_clan[chat_id]:
                bot.reply_to(message, "❌ Пользователь уже состоит в клане.")
                return
            if target_id not in clans[chat_id][clan_name]["members"]:
                clans[chat_id][clan_name]["members"].append(target_id)
            if chat_id not in user_clan: user_clan[chat_id] = {}
            user_clan[chat_id][target_id] = clan_name
            bot.reply_to(message, f"✅ Пользователь добавлен в клан **{clan_name}**!")
            return

        if subcmd == "выйти":
            if chat_id not in user_clan or user_id not in user_clan[chat_id]:
                bot.reply_to(message, "❌ Вы не состоите в клане.")
                return
            clan_name = user_clan[chat_id][user_id]
            if clans[chat_id][clan_name]["leader"] == user_id:
                bot.reply_to(message, "❌ Лидер не может выйти. Передайте лидерство или распустите клан.")
                return
            clans[chat_id][clan_name]["members"].remove(user_id)
            del user_clan[chat_id][user_id]
            bot.reply_to(message, f"✅ Вы вышли из клана **{clan_name}**.")
            return

        if subcmd == "информация":
            if chat_id not in user_clan or user_id not in user_clan[chat_id]:
                bot.reply_to(message, "❌ Вы не состоите в клане.")
                return
            clan_name = user_clan[chat_id][user_id]
            clan = clans[chat_id][clan_name]
            leader_name = stats[chat_id].get(clan["leader"], {}).get("name", "Неизвестно")
            members_names = [stats[chat_id].get(m, {}).get("name", f"ID {m}") for m in clan["members"]]
            txt = f"🏰 **Клан: {clan_name}**\n👑 Лидер: {leader_name}\n👥 Участники ({len(members_names)}):\n" + "\n".join(f"• {m}" for m in members_names)
            bot.reply_to(message, txt, parse_mode="Markdown")
            return

        bot.reply_to(message, "❌ Неизвестная подкоманда. Используйте: создать, пригласить, выйти, информация.")
        return

    # === ОБЩИЕ КОМАНДЫ (ПО ПОЛОЧКАМ) ===
    if text_lower == "команды":
        commands_list = (
            "📋 **Команды (по полочкам):**\n\n"
            "💰 **Экономика:**\n"
            "• `баланс` — монеты\n"
            "• `перевести <сумма> <@username>` — перевод\n"
            "• `магазин` — товары\n"
            "• `купить <название>` — купить\n"
            "• `инвентарь` — покупки\n"
            "• `поставить <название>` — экипировка\n\n"
            "🎰 **Казино:**\n"
            "• `казино` — игра (ставка и подтверждение)\n\n"
            "💼 **Бизнесы:**\n"
            "• `купить бизнес` — меню бизнесов (в ЛС)\n\n"
            "🎟 **Промокоды:**\n"
            "• `промокод <код>` — активировать (в ЛС)\n\n"
            "🏰 **Кланы:**\n"
            "• `клан создать <название>`\n"
            "• `клан пригласить <@username>`\n"
            "• `клан выйти`\n"
            "• `клан информация`\n\n"
            "📊 **Статистика:**\n"
            "• `стата` / `топ` — топ активных\n"
            "• `профиль` — профиль\n\n"
            "🎭 **РП-команды:**\n" + "\n".join([f"• `{cmd}`" for cmd in rp_commands]) + "\n\n"
            "👑 **Для админа:**\n"
            "• `+монеты <сумма> <@username>` — выдать монеты\n"
            "• `/give <@username|ID> <сумма>` — выдать монеты\n"
            "• `баланс-админ [@username|все]` — посмотреть баланс\n"
            "• `/promo <код> <тип> <название> <кол-во>` — создать промокод\n\n"
            "📌 **Прочее:**\n"
            "• `команды` — этот список"
        )
        bot.send_message(chat_id, commands_list, parse_mode="Markdown")
        return

    if text_lower == "баланс":
        bot.reply_to(message, f"💰 У {user_name} **{get_balance(chat_id, user_id)}** монет.", parse_mode="Markdown")
        return

    if text_lower == "магазин":
        shop_text = (
            "🛒 **Магазин:**\n\n"
            "🐾 **Персонажи:**\n" + format_shop_items("pet") +
            "\n🚗 **Машины:**\n" + format_shop_items("car") +
            "\n🏠 **Дома:**\n" + format_shop_items("house") +
            "\nКупить: `купить <название>`\n"
            "🏢 **Бизнесы:** `купить бизнес` (в ЛС)"
        )
        bot.send_message(chat_id, shop_text, parse_mode="Markdown")
        return

    if text_lower == "инвентарь":
        if chat_id in inventory and user_id in inventory[chat_id] and inventory[chat_id][user_id]:
            items = inventory[chat_id][user_id]
            text_inv = "🎒 **Твои покупки:**\n\n"
            for item_name in items:
                item = SHOP_ITEMS.get(item_name)
                if item:
                    text_inv += f"{item['emoji']} **{item_name.capitalize()}** — {item['desc']}\n"
            biz_items = [b for b in items if b in BUSINESSES]
            if biz_items:
                text_inv += "\n💼 **Бизнесы:**\n"
                for b in biz_items:
                    text_inv += f"{BUSINESSES[b]['emoji']} **{b.capitalize()}** — доход {BUSINESSES[b]['income']} 🪙/час\n"
            bot.reply_to(message, text_inv, parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ У тебя пока ничего нет. Загляни в `магазин`!")
        return

    if text_lower.startswith("перевести "):
        parts = text.split()
        if len(parts) < 3:
            bot.reply_to(message, "❌ Формат: `перевести <сумма> <@username>`")
            return
        try: amount = int(parts[1])
        except: bot.reply_to(message, "❌ Сумма — число."); return
        target_username = parts[2].replace("@", "").lower()
        target_id = target_name = None
        for uid, data in stats[chat_id].items():
            if data["name"].lower() == f"@{target_username}":
                target_id, target_name = uid, data["name"]; break
        if target_id is None: bot.reply_to(message, "❌ Пользователь не найден."); return
        if target_id == user_id: bot.reply_to(message, "❌ Себе нельзя."); return
        if get_balance(chat_id, user_id) < amount: bot.reply_to(message, "❌ Мало монет."); return
        if amount <= 0: bot.reply_to(message, "❌ Сумма > 0."); return
        add_coins(chat_id, user_id, -amount)
        add_coins(chat_id, target_id, amount)
        bot.reply_to(message, f"💸 {user_name} перевёл **{amount}** 🪙 {target_name}!", parse_mode="Markdown")
        return

    if text_lower.startswith("купить "):
        item_name = text_lower[7:].strip()
        if item_name == "бизнес":
            bot.reply_to(message, "🛒 Зайдите в ЛС бота и напишите `купить бизнес`.")
            return
        if item_name not in SHOP_ITEMS:
            bot.reply_to(message, "❌ Нет такого товара.")
            return
        price = SHOP_ITEMS[item_name]["price"]
        if get_balance(chat_id, user_id) < price:
            bot.reply_to(message, f"❌ Нужно {price} 🪙, у тебя {get_balance(chat_id, user_id)} 🪙.")
            return
        if chat_id not in inventory: inventory[chat_id] = {}
        if user_id not in inventory[chat_id]: inventory[chat_id][user_id] = []
        if item_name in inventory[chat_id][user_id]:
            bot.reply_to(message, "❌ Уже есть.")
            return
        add_coins(chat_id, user_id, -price)
        inventory[chat_id][user_id].append(item_name)
        bot.reply_to(message, f"✅ {user_name} купил {SHOP_ITEMS[item_name]['emoji']} **{item_name.capitalize()}** за {price} 🪙!", parse_mode="Markdown")
        return

    if text_lower.startswith("поставить "):
        item_name = text_lower[10:].strip()
        if item_name not in SHOP_ITEMS: bot.reply_to(message, "❌ Нет такого."); return
        item = SHOP_ITEMS[item_name]
        if chat_id not in inventory or user_id not in inventory[chat_id] or item_name not in inventory[chat_id][user_id]:
            bot.reply_to(message, "❌ Сначала купи."); return
        if item["type"] == "pet": bot.reply_to(message, "❌ Персонажей не ставим."); return
        set_equipped(chat_id, user_id, item["type"], item_name)
        bot.reply_to(message, f"✅ {user_name} поставил {item['emoji']} **{item_name.capitalize()}**!", parse_mode="Markdown")
        return

    if text_lower.startswith("казино"):
        parts = text_lower.split()
        if len(parts) == 1:
            user_states[chat_id] = f"waiting_for_bet:{user_id}"
            bot.reply_to(message, "🎰 **Введите ставку** (число):")
            return
        else:
            try:
                bet = int(parts[1])
                if bet <= 0: bot.reply_to(message, "❌ Ставка > 0."); return
                if get_balance(chat_id, user_id) < bet: bot.reply_to(message, "❌ Мало монет."); return
                markup = types.InlineKeyboardMarkup()
                markup.add(
                    types.InlineKeyboardButton("✅ Подтвердить", callback_data=f"confirmbet|{user_id}|{bet}"),
                    types.InlineKeyboardButton("❌ Отмена", callback_data=f"cancelbet|{user_id}")
                )
                bot.reply_to(message, f"🎰 Подтвердите ставку **{bet}** 🪙?", reply_markup=markup, parse_mode="Markdown")
            except ValueError:
                bot.reply_to(message, "❌ Ставка — число.")
            return

    if text_lower in ["стата", "топ", "профиль"]:
        if chat_id not in stats or not stats[chat_id]:
            bot.send_message(chat_id, "📊 Нет статистики.")
            return
        if text_lower == "профиль" or message.reply_to_message:
            target = message.reply_to_message.from_user if message.reply_to_message else message.from_user
            target_id = target.id
            target_name = get_user_name(target)
            if target_id in stats[chat_id]:
                c = stats[chat_id][target_id]["count"]
                l = stats[chat_id][target_id]["late"]
                r = get_user_rank(c)
                coins = get_balance(chat_id, target_id)
                inv_items = inventory.get(chat_id, {}).get(target_id, [])
                txt = (
                    f"👤 **Профиль:** {target_name}\n"
                    f"💬 **Сообщений:** {c}\n"
                    f"⏰ **Опозданий:** {l}\n"
                    f"🏅 **Ранг:** {r}\n"
                    f"💰 **Монет:** {coins} 🪙\n"
                )
                eq = equipped.get(chat_id, {}).get(target_id, {})
                if "car" in eq:
                    car_item = SHOP_ITEMS.get(eq["car"])
                    if car_item: txt += f"🚗 **Машина:** {car_item['emoji']} {eq['car'].capitalize()}\n"
                if "house" in eq:
                    house_item = SHOP_ITEMS.get(eq["house"])
                    if house_item: txt += f"🏠 **Дом:** {house_item['emoji']} {eq['house'].capitalize()}\n"
                if inv_items:
                    txt += "🎒 **Покупки:**\n"
                    for item_name in inv_items:
                        item = SHOP_ITEMS.get(item_name)
                        if item: txt += f"  {item['emoji']} {item_name.capitalize()}\n"
                biz_items = [b for b in inv_items if b in BUSINESSES]
                if biz_items:
                    txt += "💼 **Бизнесы:**\n"
                    for b in biz_items:
                        txt += f"  {BUSINESSES[b]['emoji']} {b.capitalize()} (+{BUSINESSES[b]['income']} 🪙/час)\n"
                txt += "🎖 **Награды:**\n"
                if c >= 10: txt += "• 🥉 Первые шаги\n"
                if c >= 100: txt += "• 🥈 Завсегдатай\n"
                if c >= 500: txt += "• 🥇 Ветеран чата\n"
                if c < 10: txt += "• Пока нет\n"
                bot.send_message(chat_id, txt, parse_mode="Markdown")
            else:
                bot.reply_to(message, "❌ Нет статистики.")
            return
        sorted_users = sorted(stats[chat_id].values(), key=lambda x: x['count'], reverse=True)[:10]
        reply = "📊 **Топ актива:**\n\n"
        for i, u in enumerate(sorted_users, 1):
            reply += f"{i}. {u['name']} — {u['count']} сообщ. {get_user_rank(u['count'])}\n"
        bot.send_message(chat_id, reply, parse_mode="Markdown")
        return

    if text_lower in rp_commands:
        if not message.reply_to_message:
            bot.reply_to(message, f"❌ `{text_lower}` — ответьте на сообщение.")
            return
        u1 = get_user_name(message.from_user)
        u2 = get_user_name(message.reply_to_message.from_user)
        bot.send_message(chat_id, rp_commands[text_lower].format(user1=u1, user2=u2))
        return

# ================= ВВОД СТАВКИ В ЧАТЕ =================
@bot.message_handler(func=lambda msg: msg.chat.type in ['group', 'supergroup'] and msg.chat.id in user_states and user_states[msg.chat.id].startswith("waiting_for_bet:"))
def process_bet_input(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    state = user_states.get(chat_id)
    if not state: return
    _, expected_user_id = state.split(":")
    if str(user_id) != expected_user_id: return
    try:
        bet = int(message.text.strip())
        if bet <= 0: bot.reply_to(message, "❌ Ставка > 0."); return
        if get_balance(chat_id, user_id) < bet: bot.reply_to(message, "❌ Мало монет."); return
        del user_states[chat_id]
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("✅ Подтвердить", callback_data=f"confirmbet|{user_id}|{bet}"),
            types.InlineKeyboardButton("❌ Отмена", callback_data=f"cancelbet|{user_id}")
        )
        bot.reply_to(message, f"🎰 Подтвердите ставку **{bet}** 🪙?", reply_markup=markup, parse_mode="Markdown")
    except ValueError:
        bot.reply_to(message, "❌ Введите число.")

# ================= ОБРАБОТЧИК КНОПОК =================
@bot.callback_query_handler(func=lambda call: call.data.startswith(("confirmbet|", "cancelbet|", "bet|", "buybiz|", "changebet|", "betcar|", "bethouse|", "betbiz|", "placeitem|")))
def handle_callbacks(call):
    data = call.data.split("|")
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    user_name = get_user_name(call.from_user)

    if data[0] == "confirmbet":
        target_user_id = int(data[1]); bet = int(data[2])
        if user_id != target_user_id: bot.answer_callback_query(call.id, "❌ Это не ваша кнопка!"); return
        if get_balance(chat_id, user_id) < bet: bot.answer_callback_query(call.id, "❌ Мало монет!"); return
        markup = types.InlineKeyboardMarkup(row_width=4)
        markup.add(
            types.InlineKeyboardButton("x2", callback_data=f"bet|x2|{user_id}|{bet}"),
            types.InlineKeyboardButton("x4", callback_data=f"bet|x4|{user_id}|{bet}"),
            types.InlineKeyboardButton("x6", callback_data=f"bet|x6|{user_id}|{bet}"),
            types.InlineKeyboardButton("x10", callback_data=f"bet|x10|{user_id}|{bet}")
        )
        markup.add(
            types.InlineKeyboardButton("🔄 Сменить ставку", callback_data=f"changebet|{user_id}"),
            types.InlineKeyboardButton("🚗 Поставить машину", callback_data=f"betcar|{user_id}|{bet}"),
            types.InlineKeyboardButton("🏠 Поставить дом", callback_data=f"bethouse|{user_id}|{bet}"),
            types.InlineKeyboardButton("💼 Поставить бизнес", callback_data=f"betbiz|{user_id}|{bet}")
        )
        try:
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=f"🎰 **Ставка: {bet} 🪙**\nВыберите множитель или имущество:", reply_markup=markup, parse_mode="Markdown")
        except Exception:
            bot.send_message(chat_id, f"🎰 **Ставка: {bet} 🪙**", reply_markup=markup, parse_mode="Markdown")
        return

    if data[0] == "cancelbet":
        if user_id != int(data[1]): bot.answer_callback_query(call.id, "❌ Не ваша кнопка!"); return
        try: bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text="❌ Ставка отменена.")
        except: pass
        return

    if data[0] == "changebet":
        if user_id != int(data[1]): bot.answer_callback_query(call.id, "❌ Не ваша кнопка!"); return
        user_states[chat_id] = f"waiting_for_bet:{user_id}"
        try: bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text="🎰 Введите новую ставку (число):")
        except: bot.send_message(chat_id, "🎰 Введите новую ставку (число):")
        return

    if data[0] == "bet":
        multiplier_str = data[1]; target_user_id = int(data[2]); bet = int(data[3])
        if user_id != target_user_id: bot.answer_callback_query(call.id, "❌ Не ваша кнопка!"); return
        if get_balance(chat_id, user_id) < bet: bot.answer_callback_query(call.id, "❌ Мало монет!"); return
        odds = {"x2": (2, 0.45, 0.05), "x4": (4, 0.20, 0.03), "x6": (6, 0.12, 0.02), "x10": (10, 0.06, 0.01)}
        if multiplier_str not in odds: return
        multiplier, win_chance, jackpot_chance = odds[multiplier_str]
        add_coins(chat_id, user_id, -bet)
        roll = random.random()
        if roll < win_chance:
            win = bet * multiplier; add_coins(chat_id, user_id, win)
            new_text = f"🎰 **Выигрыш!** {user_name} ставил {bet} на **{multiplier_str}** и получил **{win}** 🪙!\n💰 Баланс: {get_balance(chat_id, user_id)} 🪙"
        elif roll < win_chance + jackpot_chance:
            win = bet * multiplier * 2; add_coins(chat_id, user_id, win)
            new_text = f"💎 **ДЖЕКПОТ!** {user_name} ставил {bet} на **{multiplier_str}** и сорвал **{win}** 🪙!\n💰 Баланс: {get_balance(chat_id, user_id)} 🪙"
        else:
            new_text = f"😢 **Проигрыш.** {user_name} ставил {bet} на **{multiplier_str}** и потерял монеты.\n💰 Баланс: {get_balance(chat_id, user_id)} 🪙"
        try: bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=new_text, parse_mode="Markdown")
        except: bot.send_message(chat_id, new_text, parse_mode="Markdown")
        return

    if data[0] in ["betcar", "bethouse", "betbiz"]:
        target_user_id = int(data[1])
        if user_id != target_user_id: bot.answer_callback_query(call.id, "❌ Не ваша кнопка!"); return
        item_type = {"betcar": "car", "bethouse": "house", "betbiz": "business"}[data[0]]
        items = inventory.get(chat_id, {}).get(user_id, [])
        if item_type == "car": available = [i for i in items if i in SHOP_ITEMS and SHOP_ITEMS[i]["type"] == "car"]
        elif item_type == "house": available = [i for i in items if i in SHOP_ITEMS and SHOP_ITEMS[i]["type"] == "house"]
        else: available = [i for i in items if i in BUSINESSES]
        if not available:
            bot.answer_callback_query(call.id, f"❌ У вас нет {'машины' if item_type == 'car' else 'дома' if item_type == 'house' else 'бизнеса'} для ставки!")
            return
        markup = types.InlineKeyboardMarkup(row_width=1)
        for item in available:
            if item_type == "business": emoji, price = BUSINESSES[item]["emoji"], BUSINESSES[item]["price"]
            else: emoji, price = SHOP_ITEMS[item]["emoji"], SHOP_ITEMS[item]["price"]
            markup.add(types.InlineKeyboardButton(f"{emoji} {item.capitalize()} ({price} 🪙)", callback_data=f"placeitem|{item_type}|{item}|{user_id}"))
        try:
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text="🎰 Выберите имущество (если проиграете — сгорит):", reply_markup=markup)
        except: bot.send_message(chat_id, "🎰 Выберите имущество:", reply_markup=markup)
        return

    if data[0] == "placeitem":
        item_type, item_name, target_user_id = data[1], data[2], int(data[3])
        if user_id != target_user_id: bot.answer_callback_query(call.id, "❌ Не ваша кнопка!"); return
        if item_name not in inventory.get(chat_id, {}).get(user_id, []): bot.answer_callback_query(call.id, "❌ Предмет не найден!"); return
        item_price = BUSINESSES[item_name]["price"] if item_type == "business" else SHOP_ITEMS[item_name]["price"]
        roll = random.random()
        if roll < 0.5:
            add_coins(chat_id, user_id, item_price)
            new_text = f"🎰 **УДАЧА!** {user_name} поставил {item_name} и выиграл **{item_price}** 🪙!\n💰 Баланс: {get_balance(chat_id, user_id)} 🪙"
        else:
            inventory[chat_id][user_id].remove(item_name)
            new_text = f"💔 **ПРОИГРЫШ!** {user_name} поставил {item_name} и потерял его!"
        try: bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=new_text, parse_mode="Markdown")
        except: bot.send_message(chat_id, new_text, parse_mode="Markdown")
        return

    if data[0] == "buybiz":
        business_name = data[1]; group_chat_id = int(data[2])
        if business_name not in BUSINESSES: bot.answer_callback_query(call.id, "❌ Бизнес не найден."); return
        price = BUSINESSES[business_name]["price"]
        if get_balance(group_chat_id, user_id) < price:
            bot.answer_callback_query(call.id, f"❌ Мало монет! Нужно {price} 🪙, у тебя {get_balance(group_chat_id, user_id)} 🪙."); return
        if group_chat_id not in inventory: inventory[group_chat_id] = {}
        if user_id not in inventory[group_chat_id]: inventory[group_chat_id][user_id] = []
        if business_name in inventory[group_chat_id][user_id]: bot.answer_callback_query(call.id, "❌ Уже есть."); return
        add_coins(group_chat_id, user_id, -price)
        inventory[group_chat_id][user_id].append(business_name)
        bot.answer_callback_query(call.id, f"✅ Куплено {business_name.capitalize()} за {price} 🪙!")
        try:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"✅ Ты купил **{business_name.capitalize()}** за {price} 🪙!\nДоход: +{BUSINESSES[business_name]['income']} 🪙/час", parse_mode="Markdown")
        except: pass
        return

# ================= ЛС: БИЗНЕС И ПРОМОКОДЫ =================
@bot.message_handler(func=lambda msg: msg.chat.type == 'private' and (msg.text and msg.text.lower() == "купить бизнес"))
def handle_biz_private(message):
    user_id = message.from_user.id
    found_chat = None
    for cid, users in stats.items():
        if user_id in users: found_chat = cid; break
    if not found_chat: bot.send_message(message.chat.id, "❌ Я не нашёл тебя ни в одном чате."); return
    show_business_menu(message.chat.id, user_id)

@bot.message_handler(func=lambda msg: msg.chat.type == 'private' and (msg.text and msg.text.lower().startswith("промокод ")))
def handle_promo_activate(message):
    user_id = message.from_user.id
    code = message.text.lower().split(" ", 1)[1].strip()
    if code not in promocodes: bot.send_message(message.chat.id, "❌ Промокод не найден."); return
    promo = promocodes[code]
    found_chat = None
    for cid, users in stats.items():
        if user_id in users: found_chat = cid; break
    if not found_chat: bot.send_message(message.chat.id, "❌ Я не нашёл тебя ни в одном чате."); return
    if promo["count"] <= 0: bot.send_message(message.chat.id, "❌ Промокод уже использован."); return
    ptype, pname = promo["type"], promo["name"]
    if ptype == "money":
        add_coins(found_chat, user_id, int(pname))
        bot.send_message(message.chat.id, f"✅ Промокод активирован! Ты получил **{pname}** 🪙!", parse_mode="Markdown")
    elif ptype == "car":
        if pname not in SHOP_ITEMS: bot.send_message(message.chat.id, "❌ Ошибка промокода."); return
        if found_chat not in inventory: inventory[found_chat] = {}
        if user_id not in inventory[found_chat]: inventory[found_chat][user_id] = []
        inventory[found_chat][user_id].append(pname)
        bot.send_message(message.chat.id, f"✅ Промокод активирован! Ты получил {SHOP_ITEMS[pname]['emoji']} **{pname.capitalize()}**!")
    elif ptype == "house":
        if pname not in SHOP_ITEMS: bot.send_message(message.chat.id, "❌ Ошибка промокода."); return
        if found_chat not in inventory: inventory[found_chat] = {}
        if user_id not in inventory[found_chat]: inventory[found_chat][user_id] = []
        inventory[found_chat][user_id].append(pname)
        bot.send_message(message.chat.id, f"✅ Промокод активирован! Ты получил {SHOP_ITEMS[pname]['emoji']} **{pname.capitalize()}**!")
    elif ptype == "business":
        if pname not in BUSINESSES: bot.send_message(message.chat.id, "❌ Ошибка промокода."); return
        if found_chat not in inventory: inventory[found_chat] = {}
        if user_id not in inventory[found_chat]: inventory[found_chat][user_id] = []
        inventory[found_chat][user_id].append(pname)
        bot.send_message(message.chat.id, f"✅ Промокод активирован! Ты получил {BUSINESSES[pname]['emoji']} **{pname.capitalize()}**!")
    promocodes[code]["count"] -= 1
    if promocodes[code]["count"] <= 0: del promocodes[code]

if __name__ == "__main__":
    print("Бот запущен...")
    bot.infinity_polling()