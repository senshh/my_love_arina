import asyncio
import logging
import random
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties
# --- КОНФИГУРАЦИЯ ---
API_TOKEN = os.getenv('API_TOKEN')
TARGET_ADMIN_ID = 6324989741  # ID человека, который должен отвечать (число)
ACCEPT_TIMEOUT = 60          # 60 секунд на нажатие кнопки "Принять"
ANSWER_TIMEOUT = 300         # 5 минут на написание текста
# Список ID пользователей, которым разрешено пользоваться ботом
# Добавьте сюда ID друзей через запятую
ALLOWED_USERS = [
    6324989741,  # Ваш ID (обязательно добавьте себя)
    5648419861,  # ID Арины
    1767978286   # ID для теста
]
# Список случайных ответов, если админ молчит
RANDOM_ANSWERS = [
    "Сама вселенная говорит ДА, при виде тебя ",
    "Для меня ты ассоциируешься с мечтой",
    "Твои волосы сегодня лежат великолепно",
    "Чтобы оценить тебя из 10, 10 не хватит ",
    "Каждый раз тону, в красоте твоих глаз)", 
    "От тебя невозможно отвести взгляд 😍",
    "Ты безупречна по своей сути 😊",
    "У тебя роскошные реснички)",
    "Ты выглядишь так, будто хочешь, чтобя я сошел от тебя с ума 🤪",
    "<tg-spoiler>Твоя попа настолько сочная, что у меня всегда полный рот слюней 😏</tg-spoiler>",
    "Когда ты говоришь, я наслаждаюсь каждой секундой, слушая тебя",
    "Ты как всегда, неотразима ❤",
    "Важный факт: Ты самая лучшая девушка",
    "Ради тебя, я сделаю что угодно",
    "Чай лучше всего пить с тобой, ведь ты такая сладкая",
    "Каждой твоей фотографией, можно наслаждаться вечно",
    "Ты секси 🥵",
    "О моя госпожа (¬‿¬)",
    "Мне невозможно перестать делать тебе комплименты)",
    "Падаю на колени, потому что ты бесподобна 😇",
    "Нету предела твоего совершенства 👀 (03.07.2025 3:05)",
    "Ты горяча, как чай в кипятке, только об тебя я только рад обжечь язык ",
    "О таких красивых лапках как у тебя, все могут только мечтать)",
    "Кстати, Я не смогу без твоей заботы и нежности (✪ ω ✪)",
    "Нет никого красивее тебя ヾ(≧ ▽ ≦)ゝ",
    "О такой девушке как ты, можно только мечтать",
    "https://telegra.ph/3-10-25-3 напоминаю <3",
    "Сердце замирает, как только вижу тебя",
    "Если ты не знала, ты бесподобна 🤩",
    "<tg-spoiler>От твоих сисичек невозможно оторваться 🤗</tg-spoiler>",
    "Помни, ты умничка, у тебя все получится 😉",
    "Знай, ТЫ лучше что со мной случалось...",
    "С каждым днем, я влюбляюсь в тебя все сильнее, и заново влюбляться не нужно)",
    "Обожаю смотреть твои репосты)",
    "Ты безумно интересная",
    "I used to think that humans are better (I mean, i'm a human) \n But now i know horses are better (Yeehaw!) \n I used to think that humans are better (But then, what?) \n Now i know that horses are better (Yeehaw!) \n Can you jump like this? \n No, i can't \n Can you run like this? \n No, i can't \n Can you stand like this? \n No, i can't \n Can you run like this? \n No, i can't ",
    "Fight, babe, I'll fight \n To win back your love again \n I will be there \n I will be there",
    "Любуясь твоими глазами, я вижу самое теплое, яркое лето 😍",
    "На тебя невозможно обижаться)",
    "Ты моё счастье 😊",
    "Ты выглядишь, точно сошла с небес😇",
    "<tg-spoiler>Ты такая трогательная, трогал бы и трогал</tg-spoiler>",
    "Для тебя не существует периода ПРАЙМ, ты всегда идеальна"
]

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

active_requests = {}
usernames_cache = {}
usernames_cache['@mademoiselle_ar'] = 5648419861
usernames_cache['@filimonrobot'] = 1767978286
def is_allowed(user_id: int) -> bool:
    return user_id in ALLOWED_USERS or user_id == TARGET_ADMIN_ID


def get_ask_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="> Получить ещё комплимент <", callback_data="ask_question")]
    ])


def get_admin_decision_kb(user_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Принять (60с)", callback_data=f"adm_accept_{user_id}"),
            InlineKeyboardButton(text="Отправить случайный", callback_data=f"adm_decline_{user_id}")
        ]
    ])


# --- ЛОГИКА ТАЙМЕРОВ ---

async def send_auto_compliment(user_id, reason_text=None):
    random_answer = random.choice(RANDOM_ANSWERS)
    message_text = f"{reason_text}\n\n{random_answer}" if reason_text else random_answer
    try:
        await bot.send_message(user_id, message_text, parse_mode="HTML", reply_markup=get_ask_keyboard())
    except Exception:
        pass
    if TARGET_ADMIN_ID in active_requests:
        del active_requests[TARGET_ADMIN_ID]


async def wait_for_acceptance(user_id: int):
    try:
        await asyncio.sleep(ACCEPT_TIMEOUT)
        if TARGET_ADMIN_ID in active_requests and active_requests[TARGET_ADMIN_ID]["user_id"] == user_id:
            await send_auto_compliment(user_id)
            await bot.send_message(TARGET_ADMIN_ID, "⏰ Время на принятие запроса истекло.")
    except asyncio.CancelledError:
        pass


async def wait_for_answer(user_id: int):
    try:
        await asyncio.sleep(ANSWER_TIMEOUT)
        if TARGET_ADMIN_ID in active_requests and active_requests[TARGET_ADMIN_ID]["user_id"] == user_id:
            await send_auto_compliment(user_id)
            await bot.send_message(TARGET_ADMIN_ID, "⏰ 5 минут истекли. Отправлен авто-ответ.")
    except asyncio.CancelledError:
        pass


# --- ХЕНДЛЕРЫ ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if not is_allowed(message.from_user.id):
        await message.answer(f"У вас нет доступа. ⛔️\nВаш ID: {message.from_user.id}")
        return

    # Сохраняем юзернейм пользователя в кэш
    if message.from_user.username:
        usernames_cache[f"@{message.from_user.username.lower()}"] = message.from_user.id

    await message.answer("Привет! Нажми кнопку для комплимента:", reply_markup=get_ask_keyboard())


# КОМАНДА ДЛЯ АДМИНА: /send @username текст
@dp.message(Command("send"), F.from_user.id == TARGET_ADMIN_ID)
@dp.message(Command("send"), F.from_user.id == TARGET_ADMIN_ID)
async def cmd_admin_send(message: types.Message, command: CommandObject):
    if not command.args:
        await message.answer("Формат: <code>/send @username текст</code>")
        return
    # 1. Разбиваем простые аргументы, чтобы найти юзернейм
    parts = command.args.split(maxsplit=1)
    target_username = parts[0].lower()
    # 2. Получаем текст с сохранением HTML-тегов
    # Отрезаем всё, что идет после юзернейма в исходном HTML-сообщении
    if len(parts) > 1:
        # Находим, где в HTML-строке заканчивается юзернейм, и берем всё после него
        # Это сохранит <b>болд</b>, <i>курсив</i> и даже спойлеры
        text_to_send = message.html_text.split(parts[0], 1)[1].strip()
    else:
        # Если админ написал только /send @username, берем случайный комплимент
        text_to_send = random.choice(RANDOM_ANSWERS)
    users = usernames_cache
    if target_username in users:
        try:
            # Отправляем с сохранением кнопок, как в твоем коде
            await bot.send_message(
                chat_id=users[target_username], 
                text=text_to_send, 
                reply_markup=get_ask_keyboard()
            )
            await message.answer(f"✅ Отправлено пользователю {target_username} с сохранением оформления")
        except Exception as e:
            await message.answer(f"❌ Ошибка при отправке: {e}")
    else:
        await message.answer(f"❌ Пользователь {target_username} не найден в базе.")
@dp.callback_query(F.data == "ask_question")
async def ask_handler(callback: types.CallbackQuery):
    if not is_allowed(callback.from_user.id):
        await callback.answer("Доступ запрещен!", show_alert=True)
        return

    if TARGET_ADMIN_ID in active_requests:
        await callback.answer("Подбираю комплимент, подожди немного ❤️", show_alert=True)
        return

    user_id = callback.from_user.id
    task = asyncio.create_task(wait_for_acceptance(user_id))
    active_requests[TARGET_ADMIN_ID] = {"user_id": user_id, "task": task, "status": "wait_accept"}

    await bot.send_message(
        TARGET_ADMIN_ID,
        f"🔔 <b>Новый запрос!</b>\nОт: {callback.from_user.full_name}\nУ тебя 60 секунд на принятие.",
        parse_mode="HTML",
        reply_markup=get_admin_decision_kb(user_id)
    )
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Запрос отправлен... Ожидай ❤️")
    await callback.answer()


@dp.callback_query(F.data.startswith("adm_accept_"))
async def accept_handler(callback: types.CallbackQuery):
    user_id = int(callback.data.split("_")[2])

    if TARGET_ADMIN_ID in active_requests and active_requests[TARGET_ADMIN_ID]["status"] == "wait_accept":
        active_requests[TARGET_ADMIN_ID]["task"].cancel()

        task = asyncio.create_task(wait_for_answer(user_id))
        active_requests[TARGET_ADMIN_ID] = {"user_id": user_id, "task": task, "status": "wait_answer"}

        await callback.message.edit_text("✅ Принято! У тебя 5 минут на текст.")
    else:
        await callback.answer("Запрос уже недействителен.")
    await callback.answer()


@dp.callback_query(F.data.startswith("adm_decline_"))
async def decline_handler(callback: types.CallbackQuery):
    if TARGET_ADMIN_ID in active_requests:
        user_id = active_requests[TARGET_ADMIN_ID]["user_id"]
        active_requests[TARGET_ADMIN_ID]["task"].cancel()
        await send_auto_compliment(user_id)
        await callback.message.edit_text("✅ Отправлен случайный комплимент")
    await callback.answer()


@dp.message(F.from_user.id == TARGET_ADMIN_ID)
async def admin_text_handler(message: types.Message):
    if TARGET_ADMIN_ID not in active_requests or active_requests[TARGET_ADMIN_ID]["status"] != "wait_answer":
        return

    req = active_requests[TARGET_ADMIN_ID]
    req["task"].cancel()
    try:
        await message.copy_to(chat_id=req["user_id"], reply_markup=get_ask_keyboard())
        await message.answer("✅ Отправлено!")
    except Exception as e:
        await message.answer(f"Ошибка: {e}")
    del active_requests[TARGET_ADMIN_ID]


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())











