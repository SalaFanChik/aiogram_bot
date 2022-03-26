import aiogram.utils.markdown as md
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Bot, Dispatcher, types
#import ujson 
#import sys
#sys.path.append('C:\\Users\\alik2\\Desktop\\Mine\\MasterMInd_bot')
from main import dp, bot, Is_liked, client, users, companies


# создаём форму и указываем поля
class Form(StatesGroup):
    name = State() 
    last_name = State()
    age = State() 
    gender = State()
    searching_gender = State() 
    key_words = State() 
    about_me = State() 
    location = State() 
    photo = State()

class Company_Form(StatesGroup):
    company_name = State() 
    age_to_in = State()  
    key_words = State() 
    about_company = State() 
    location = State() 
    photo = State()



# Начинаем наш диалог
@dp.message_handler()
async def start(message: types.Message):
    button1 = KeyboardButton('Single')
    button2 = KeyboardButton('Company')
    markup4 = ReplyKeyboardMarkup(resize_keyboard=True).row(
        button1, button2
    )
    if message.text.lower() in ['создать анкету', 'обновить профиль']:
        await message.reply(f"Ты хочешь создать компанию людей или найти человека?", reply_markup=markup4)
    elif message.text.lower() == 'single':
        if users.find({"user_id": str(message.chat.id)}):
            #починить не работает удаление
            users.delete_one({"user_id": str(message.chat.id)})
        await Form.name.set()
        ReplyKeyboardRemove()
        await message.answer('Как тебя зовут?')
    elif message.text.lower() == 'company':
        if list(companies.find({"user_id": str(message.chat.id)})):
            companies.delete_one({"user_id": str(message.chat.id)})
            await Company_Form.company_name.set()
            ReplyKeyboardRemove()
            await message.answer('Введите название')
            print('as')
        elif not list(users.find({"user_id": str(message.chat.id)})):
            print('asd')
            await message.reply(f"Обьязательно надо зарегистрироваться как single аккаунт", reply_markup=markup4)
        else:
            await Company_Form.company_name.set()
            ReplyKeyboardRemove()
            await message.answer('Введите название')

    elif message.text == 'Узнать больше о MasterMind':
        await message.answer('''В составе мастермайнд-группы обычно от двух до шести человек. Группа встречается регулярно, например раз в две недели. Можно встречаться лично или созваниваться через Skype, Zoom или другую программу. Плюс личной встречи в том, что по пути на нее можно дополнительно обдумать то, что хочется на этот раз обсуждать, а на обратном — порефлексировать.

На каждого участника выделяется фиксированное время (например, по 20 минут), в течение которого человек рассказывает о своей проблеме, идее или задаче, просит совета или берет на себя обязательство что-нибудь сделать до следующей встречи. После этого в установленное время (например, 5 минут) остальные участники дают обратную связь спикеру в той форме, в которой ему и им это удобно

ВАЖНО ОТМЕТИТЬ:
Так же вы можете, использовать это как инструмент для поиска единномышленников
Если вы певец, и ищите гитариста, а может и хотите собрать целую группу, возможно вы режиссер, ищите актёров, а может и танцор, который ищет для себя команду.
Все это можете решить через нашего Бота....''')





# Добавляем возможность отмены, если пользователь передумал заполнять
@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await message.reply('Ок')


@dp.message_handler(state=Company_Form.company_name)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['company_name'] = message.text

    await Company_Form.next()
    await message.reply("Введите возраст участников (ср знач)")

@dp.message_handler(lambda message: not message.text.isdigit(), state=Company_Form.age_to_in)
async def process_age_invalid(message: types.Message):
    return await message.reply("Напиши коректный возраст или напиши /cancel")

@dp.message_handler(lambda message: message.text.isdigit(), state=Company_Form.age_to_in)
async def process_age(message: types.Message, state: FSMContext):
    await Company_Form.next()
    await state.update_data(age_to_in=int(message.text))

    await message.reply("напишите ключевые слова чем занимается ваша комания через запятую")


@dp.message_handler(state=Company_Form.key_words)
async def process_key_words(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['key_words'] = message.text
        await Company_Form.next()
        await message.reply("Расскажи для чего компания")

@dp.message_handler(state=Company_Form.about_company)
async def process_about_me(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['about_company'] = message.text
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add(KeyboardButton('Отправить свою локацию 🗺️', request_location=True))
        await Company_Form.next()
        await message.reply("Скинь свое местополежение или напишите свой город", reply_markup=markup)


@dp.message_handler(content_types=['location', 'text'], state=Company_Form.location)
async def process_location(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text != None:
            data['location'] = message.text
        else:
            lat = message.location.latitude
            lon = message.location.longitude
            data['location'] = f"{lat}, {lon}"

        markup = types.ReplyKeyboardRemove()
        await Company_Form.next()
        await message.reply("Скиньте изображение", reply_markup=markup)


@dp.message_handler(content_types=["photo"], state=Company_Form.photo)
async def get_photo(message: types.Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    button1 = KeyboardButton('Мой профиль')
    button2 = KeyboardButton("Поиск")
    button3 = KeyboardButton("Обновить профиль")
    button4 = KeyboardButton("Настройки")
    markup = ReplyKeyboardMarkup(resize_keyboard=True).row(
            button1, button2, button3, button4
        )
    async with state.proxy() as data:
        info = {
                "user_id": str(message.chat.id),
                "company_name": data['company_name'],
                "age": str(data['age_to_in']),
                "key_words": data['key_words'],
                "about_me": data["about_company"],
                "location": data["location"],
                "photo": file_id,
                "is_active": True,
                "recieved_from": []
            }
       
    companies.insert_one(info)

    await bot.send_message(
        message.chat.id,
        'Ваша анкета создана', 
        parse_mode=ParseMode.MARKDOWN,
        reply_markup= markup 
    )

    await state.finish()




#################
#single
#################




# Сюда приходит ответ с именем
@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text

    ReplyKeyboardRemove()
    await Form.next()
    await message.reply("Фамилия")

@dp.message_handler(state=Form.last_name)
async def process_last_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['last_name'] = message.text

    await Form.next()
    await message.reply("Сколько тебе лет?")

# Проверяем возраст
@dp.message_handler(lambda message: not message.text.isdigit(), state=Form.age)
async def process_age_invalid(message: types.Message):
    return await message.reply("Напиши возраст или напиши /cancel")

# Принимаем возраст и узнаём пол
@dp.message_handler(lambda message: message.text.isdigit(), state=Form.age)
async def process_age(message: types.Message, state: FSMContext):
    await Form.next()
    await state.update_data(age=int(message.text))

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("Парень", "Девушка")

    await message.reply("Укажи пол (кнопкой)", reply_markup=markup)


# Проверяем пол
@dp.message_handler(lambda message: message.text not in ["Парень", "Девушка"], state=Form.gender)
async def process_gender_invalid(message: types.Message):
    return await message.reply("Не знаю такой пол. Укажи пол кнопкой на клавиатуре")



@dp.message_handler(state=Form.gender)
async def process_gender(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['gender'] = message.text
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add("Парень", "Девушка", "Все равно")
        
        await Form.next()
        await message.reply("Выберите кого искать", reply_markup=markup)

@dp.message_handler(lambda message: message.text not in ["Парень", "Девушка", "Все равно"], state=Form.gender)
async def process_searching_gender_invalid(message: types.Message):
    return await message.reply("Не знаю такой пол. Укажи пол кнопкой на клавиатуре")

@dp.message_handler(state=Form.searching_gender)
async def process_searching_gender(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['searching_gender'] = message.text
        markup = types.ReplyKeyboardRemove()
        await Form.next()
        await message.reply("Напишите ключевые слова через запятую", reply_markup=markup)


@dp.message_handler(state=Form.key_words)
async def process_key_words(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['key_words'] = message.text
        await Form.next()
        await message.reply("Расскажи о себе")

@dp.message_handler(state=Form.about_me)
async def process_about_me(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['about_me'] = message.text
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add(KeyboardButton('Отправить свою локацию 🗺️', request_location=True))
        await Form.next()
        await message.reply("Скинь свое местополежение", reply_markup=markup)


@dp.message_handler(content_types=['location', 'text'], state=Form.location)
async def process_location(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text != None:
            data['location'] = message.text
        else:
            lat = message.location.latitude
            lon = message.location.longitude
            data['location'] = f"{lat}, {lon}"

        markup = types.ReplyKeyboardRemove()
        await Form.next()
        await message.reply("Скиньте изображение", reply_markup=markup)


@dp.message_handler(content_types=["photo"], state=Form.photo)
async def get_photo(message: types.Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    async with state.proxy() as data:
        info = {
                "user_id": str(message.chat.id),
                "name": data['name'],
                "last_name": data['last_name'],
                "age": str(data['age']),
                "gender": data['gender'],
                "search_gender": data["searching_gender"],
                "key_words": data['key_words'],
                "about_me": data["about_me"],
                "location": data["location"],
                "photo": file_id,
                "right_now": True,
                "is_active": True,
                "recieved_from": [],
                "send_to": [],
                "companies": [] 
            }

    users.insert_one(info)
    button1 = KeyboardButton('Мой профиль')
    button2 = KeyboardButton("Поиск")
    button3 = KeyboardButton("Создать анкету")
    button3 = KeyboardButton("Настройки")
    markup = ReplyKeyboardMarkup(resize_keyboard=True).row(
            button1, button2, button3
        )

    await bot.send_message(
        message.chat.id,
        'Ваш профиль создан, в данный момент активна ваш single профиль, можно поменять в настройках', 
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=markup
    )

    await state.finish()
    
