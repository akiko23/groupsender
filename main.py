import asyncio

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

import states
from config import dp, bot, db
from states import AllStates


def get_mkeyb():
    is_stopped = bool(int(open("is_stopped.txt", 'r', encoding="utf-8").read()))
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Рассылаемое сообщение", callback_data="sendto-groups")],
            [InlineKeyboardButton(text="Добавить группу", callback_data="add_group")],
            [InlineKeyboardButton(text="Указать интервал отправки сообщений", callback_data="set_send_interval")],
            [InlineKeyboardButton(text="Сменить аккаунт", callback_data="change_account")],
            [InlineKeyboardButton(text="Остановить рассылку", callback_data="send-stop") if not is_stopped
             else InlineKeyboardButton(text="Начать рассылку", callback_data="send-start")]
        ]
    )


@dp.message_handler(commands=['start'])
async def index(msg: types.Message):
    user_id = msg.from_user.id
    if msg.chat.type != 'private':
        user_id = f"-100{msg.from_user.id}"
    db.add_user(user_id, msg.from_user.full_name) if not db.user_exists(msg.from_user.id) else None
    await bot.send_message(msg.from_user.id, "Выберите, что хотите сделать", reply_markup=get_mkeyb())


@dp.callback_query_handler(Text(startswith="sendto"))
async def sendin_handler(call: types.CallbackQuery):
    with open("interval.txt", 'r') as f:
        interval = f.read()
    await call.message.edit_text(
        f"Отправьте сообщение, которое должно будет рассылаться в чаты с интервалом {interval}",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Отмена", callback_data="stop-process")]
            ]
        ))
    await AllStates.set_message.set()


@dp.callback_query_handler(Text("add_group"))
async def add_group_link(call: types.CallbackQuery):
    await call.message.edit_text("Отправьте ссылку на группу, чтобы добавить ее", reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Отмена", callback_data="stop-process")]
        ]
    ))
    await AllStates.add_group.set()


@dp.callback_query_handler(Text(startswith="send"))
async def process_send(call: types.CallbackQuery):
    with open("is_stopped.txt", 'w') as f:
        match call.data.split('-')[1]:
            case "stop":
                print("stop")
                f.write("1")
                with open("is_registered.txt", 'w', encoding="utf-8") as f2:
                    f.write("0")
            case "start":
                print("start")
                f.write("0")
    await call.message.edit_text("Успешно", reply_markup=InlineKeyboardMarkup(
                                   inline_keyboard=[
                                       [InlineKeyboardButton(text="В главное меню", callback_data="to_main_menu")]
                                   ]
                               ))


@dp.callback_query_handler(Text("set_send_interval"))
async def set_send_interval(call: types.CallbackQuery):
    await call.message.edit_text(
        "Введите интервал отправки сообщений в секундах(3600 секунд - 1 час, 83400 секунд - 1 день)"
        " и через каждый интервал бот будет присылать сообщения во все группы",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Отмена", callback_data="stop-process")]
            ]
        ))
    await AllStates.set_interval.set()


@dp.message_handler(content_types=['text'], state=AllStates.set_interval)
async def set_interval(msg: types.Message, state: FSMContext):
    await bot.delete_message(msg.from_user.id, msg.message_id - 1)
    try:
        interval = int(msg.text)
        with open("interval.txt", "w") as f:
            f.write(str(interval))
        await bot.send_message(msg.from_user.id, f"Интервал успешно изменен, теперь он составляет {interval} секунд",
                               reply_markup=InlineKeyboardMarkup(
                                   inline_keyboard=[
                                       [InlineKeyboardButton(text="В главное меню", callback_data="to_main_menu")]
                                   ]
                               ))
        await state.finish()
    except:
        await bot.send_message(msg.from_user.id, "Вы некорректно ввели значение", reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Отмена", callback_data="stop-process")]
            ]
        ))


@dp.message_handler(content_types=['text'], state=AllStates.add_group)
async def get_new_group_href(msg: types.Message, state: FSMContext):
    if not db.group_exists(msg.text.strip()):
        db.add_group(msg.text.strip())
        answer = "Ссылка на группу успешно добавлена"
    else:
        answer = "Такая группа уже существует"
    await state.finish()

    await bot.delete_message(msg.from_user.id, msg.message_id - 1)
    await bot.send_message(msg.from_user.id, answer, reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="В главное меню", callback_data="to_main_menu")]
        ]
    ))


# , 'photo', 'document', 'video', 'voice', 'media', 'sticker', 'animation'


@dp.message_handler(content_types=['text'],
                    state=AllStates.set_message)
async def process_message(msg: types.Message, state: FSMContext):
    with open("message.txt", 'w', encoding="utf-8") as f:
        f.write(msg.text)

    try:
        await bot.delete_message(msg.from_user.id, msg.message_id - 1)
    except:
        pass

    answer = f"Принято, текст нового сообщения: {msg.text}"

    await state.finish()
    await bot.send_message(msg.from_user.id, answer,
                           reply_markup=InlineKeyboardMarkup(
                               inline_keyboard=[
                                   [InlineKeyboardButton(text="В главное меню", callback_data="to_main_menu")]
                               ]
                           ))


@dp.callback_query_handler(Text("stop-process"), state=AllStates.all_states)
async def stop_process(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.edit_text("Вы отменили операцию", reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="В главное меню", callback_data="to_main_menu")]
        ]
    ))


@dp.callback_query_handler(Text("to_main_menu"))
async def to_main_menu(call: types.CallbackQuery):
    await call.message.edit_text("Выберите, что хотите сделать", reply_markup=get_mkeyb())


@dp.message_handler(content_types=['text', 'photo', 'document', 'video', 'voice', 'media', 'animation'])
async def sender(msg: types.Message):
    user_id = msg.from_user.id
    if msg.chat.type != 'private':
        user_id = f"-100{msg.from_user.id}"
    db.add_user(user_id, msg.from_user.full_name) if not db.user_exists(msg.from_user.id) else None


def start_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(executor.start_polling(dp, skip_updates=True))
    loop.close()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
