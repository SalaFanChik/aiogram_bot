import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ParseMode
from config import API_TOKEN, information
#import ujson 
from fuzzywuzzy import fuzz
import emoji
from geopy.geocoders import Nominatim
import pymongo
from pymongo import MongoClient
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.handler import CancelHandler
import asyncio

client = MongoClient('localhost', 27017)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
db = client['users_db']
users = db['users']

company_db = client['companies_db']
companies = company_db['companies']

class CheckBannedUsers(BaseMiddleware):
    async def on_pre_process_update(self, update: types.Update, data: dict):
        if update.message:
            if list(users.find({"user_id": str(update.message.chat.id)})):
                if not list(users.find({"user_id": str(update.message.chat.id)}))[0]['is_active'] and update.message.chat.id != 1639491822:
                    await bot.send_message(update.message.chat.id, f"Вы заблокированы напишите администратору <a href='tg://openmessage?user_id=1639491822'>Админ</a> ", parse_mode=ParseMode.HTML)
                    raise CancelHandler()


class Is_liked(StatesGroup):
    liked = State()

class for_like(StatesGroup):
    like = State()

class To_like(StatesGroup):
    to_like = State()

class Report(StatesGroup):
    reporting = State()

class Set_main_page(StatesGroup):
    main_page = State()

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    button1 = KeyboardButton('Узнать больше о MasterMind')
    button2 = KeyboardButton("Создать анкету")

    markup4 = ReplyKeyboardMarkup(resize_keyboard=True).row(
        button1, button2
    )
    await message.reply(f"{information}", reply_markup=markup4)

@dp.message_handler(commands=['ban'])
async def start(message: types.Message):
    if message.chat.id == 1639491822:
        user_for_ban = str(message.text).split(" ")[1]
        users.find_one_and_update({"user_id": f"{user_for_ban}"}, {"$set": {"is_active": False}})
        await message.reply("Пользователь был забанен")

@dp.message_handler(commands=['get'])
async def start(message: types.Message):
    if message.chat.id == 1639491822:
        await message.reply(f"{len(list(users.find({})))}")

@dp.message_handler(commands=['unban'])
async def start(message: types.Message):
    if message.chat.id == 1639491822:
        user_for_ban = str(message.text).split(" ")[1]
        print(user_for_ban)
        users.find_one_and_update({"user_id": f"{user_for_ban}"}, {"$set": {"is_active": True}})
        await message.reply("Пользователь был разбанен")


@dp.message_handler(commands=['send'])
async def start(message: types.Message):
    if message.chat.id == 1639491822:
        mes = str(message.text).replace("/send", " ")
        try:
            file_id = message.photo[-1].file_id
            for i in list(users.find({})):
                await bot.send_photo(i.get("user_id"), file_id, caption=mes)
        except:
            for i in list(users.find({})):
                await bot.send_message(i.get("user_id"), mes)
        await message.reply("Всем отправлено")


@dp.message_handler(lambda message: message.text.lower() == 'настройки')
async def settings(message: types.Message):
    button1 = KeyboardButton('Single page')
    button2 = KeyboardButton("Company page")

    markup4 = ReplyKeyboardMarkup(resize_keyboard=True).row(
        button1, button2
    )
    await Set_main_page.main_page.set()
    await message.reply(f"Какую страницу хотите сделать главной?", reply_markup=markup4)

@dp.message_handler(lambda message: message.text.lower() == 'главное меню')
async def settings(message: types.Message):
    button1 = KeyboardButton('Мой профиль')
    button2 = KeyboardButton("Поиск")
    button3 = KeyboardButton("Создать анкету")
    button4 = KeyboardButton("Настройки")
    markup = ReplyKeyboardMarkup(resize_keyboard=True).row(button1, button2, button3, button4)
    await message.reply(f"Выберите что хотите сделать?", reply_markup=markup)

@dp.message_handler(lambda message: message.text.lower() == 'поиск')
async def search_starter(message: types.Message,):
    state = dp.current_state(chat=message.chat.id, user=message.from_user.id)
    if list(users.find({"user_id": str(message.chat.id)})):
        if list(users.find({"user_id": str(message.chat.id)}))[0]['right_now']:
            await poisk(message, state)
        elif not list(users.find({"user_id": str(message.chat.id)}))[0]['right_now']:
            await poisk_company(message, state)
    else:
        button1 = KeyboardButton('Узнать больше о MasterMind')
        button2 = KeyboardButton("Создать анкету")

        markup4 = ReplyKeyboardMarkup(resize_keyboard=True).row(button1, button2)
        await message.reply("Зарегистрируйтесь", reply_markup=markup4)
@dp.message_handler(state=Set_main_page.main_page)
async def change_item(message: types.Message, state: FSMContext):
    button1 = KeyboardButton('Обновить профиль')
    button2 = KeyboardButton("Поиск")
    button3 = KeyboardButton("Мой профиль")
    markup4 = ReplyKeyboardMarkup(resize_keyboard=True).row(
        button1, button2, button3      
    )
    if message.text.lower() == "single page":
        if list(companies.find({"user_id": str(message.chat.id)})):
            users.find_one_and_update({"user_id": str(message.chat.id)}, {"$set": {"right_now": True}})
            await message.reply(f"Вы на страничке single", reply_markup=markup4)
            await state.finish()
        else:
            button1 = KeyboardButton('Узнать больше о MasterMind')
            button2 = KeyboardButton("Создать анкету")

            markup4 = ReplyKeyboardMarkup(resize_keyboard=True).row(button1, button2)
            await message.reply("Зарегистрируйтесь", reply_markup=markup4)
    elif message.text.lower() == "company page":
        if list(companies.find({"user_id": str(message.chat.id)})):
            users.find_one_and_update({"user_id": str(message.chat.id)}, {"$set": {"right_now": False}})
            await message.reply(f"Вы на страничке company", reply_markup=markup4)
            await state.finish()
        else:
            button1 = KeyboardButton('Узнать больше о MasterMind')
            button2 = KeyboardButton("Создать анкету")

            markup4 = ReplyKeyboardMarkup(resize_keyboard=True).row(button1, button2)
            await message.reply("Зарегистрируйтесь", reply_markup=markup4)
    elif message.text.lower() == "главное меню":
        button1 = KeyboardButton('Мой профиль')
        button2 = KeyboardButton("Поиск")
        button3 = KeyboardButton("Создать анкету")
        button4 = KeyboardButton("Настройки")
        markup = ReplyKeyboardMarkup(resize_keyboard=True).row(
                button1, button2, button3, button4
            )
        await message.reply(f"Выберите что хотите сделать?", reply_markup=markup)
        await state.finish()
    else:
        button1 = KeyboardButton('Single page')
        button2 = KeyboardButton("Company page")
        button2 = KeyboardButton("Главное меню")
        markup2 = ReplyKeyboardMarkup(resize_keyboard=True).row(
            button1, button2
        )
        await message.reply(f"Некоректная опция", reply_markup=markup2)

@dp.message_handler(lambda message: message.text.lower() == 'мой профиль')
async def my_profile(message: types.Message):
    button1 = KeyboardButton('Обновить профиль')
    button2 = KeyboardButton("Поиск")
   #button3 = KeyboardButton("Поиск компании")
    markup4 = ReplyKeyboardMarkup(resize_keyboard=True).row(
        button1, button2    
    )


    try:
        profile = list(users.find({"user_id": str(message.chat.id)}))[0]
        if profile['right_now']:
            try:
                city2 = str(geolocator.reverse(profile['location'])).split(",")[0]
            except:
                pass            
            await bot.send_photo(chat_id=message.chat.id, photo=profile['photo'], caption=f"{profile['last_name']} {profile['name']},{profile['age']}, {profile['location']}\n\n {profile['about_me']}", reply_markup=markup4) 
        else:
            profile = list(companies.find({"user_id": str(message.chat.id)}))[0]
            try:
                city2 = str(geolocator.reverse(profile['location'])).split(",")[0]
            except:
                pass            
            await bot.send_photo(chat_id=message.chat.id, photo=profile['photo'], caption=f"{profile['company_name']}, {profile['location']}\n\n {profile['about_me']}", reply_markup=markup4) 

    except TypeError:
        profile = list(companies.find({"user_id": str(message.chat.id)}))[0]
        try:
            city2 = str(geolocator.reverse(profile['location'])).split(",")[0]
        except:
            pass            
        await bot.send_photo(chat_id=message.chat.id, photo=profile['photo'], caption=f"{profile['company_name']}, {profile['location']}\n\n {profile['about_me']}", reply_markup=markup4) 
    except Exception as e:
        print(e)
        button34 = KeyboardButton("Создать анкету")
        markup6 = ReplyKeyboardMarkup(resize_keyboard=True).row(button34)
        await message.answer('Зарегистрируйся', reply_markup=markup6)



async def poisk_company(message: types.Message, state: FSMContext):
    caller_id = str(message.chat.id)
    data = list(users.find({"user_id": str(message.chat.id)}))[0]
    global company_id
    button1 = KeyboardButton("👍")
    button2 = KeyboardButton("👎")
    button3 = KeyboardButton("Репорт")
    button4 = KeyboardButton("Главное меню")
    geolocator = Nominatim(user_agent="geoapiExercises")
    age = data['age']
    city = data['location']
    key_words = [x.lower() for x in data['key_words']]
    markup4 = ReplyKeyboardMarkup(resize_keyboard=True).row(button1, button2, button3, button4)
    if not city.isalpha():
        city = str(geolocator.reverse(city)).split(',')[0]
    for company in companies.find({"user_id":{"$ne":caller_id}}):
        company_sought_for = company['user_id']
        if company_sought_for not in data['companies']:
            if abs(int(age) - int(company['age'])) <= 5:
                city2 = data['location']
                try:
                    city2 = str(geolocator.reverse(city2)).split(",")[0]
                except:
                    pass
                if fuzz.ratio(city, city2) > 60:
                    key_words2 = [x.lower() for x in company['key_words']]
                    result=list(set(key_words) & set(key_words2))
                    if result:
                        await bot.send_photo(chat_id=message.chat.id, photo=company['photo'], caption=f"{company['company_name']}, {city2}\n\n {company['about_me']}", reply_markup=markup4) 
                        await To_like.to_like.set()
                        async with state.proxy() as data:
                            data['id_caller'] = caller_id
                            data['company_sought_for'] = company_sought_for
                        break

@dp.message_handler(state=To_like.to_like)
async def process_like_company(message: types.Message, state: FSMContext):
    button1 = KeyboardButton("Посмотреть")
    markup4 = ReplyKeyboardMarkup(resize_keyboard=True).row(button1)
    state = dp.current_state(chat=message.chat.id, user=message.from_user.id)
    async with state.proxy() as dat:
        caller_id = dat['id_caller']
        company_sought_for = dat['company_sought_for']
    data = list(companies.find({"user_id": company_sought_for}))[0]
    if message.text == "👍":
        companies.update_one({'user_id': company_sought_for}, {'$push': {'recieved_from': caller_id}})
        users.update_one({'user_id': caller_id}, {'$push': {'companies': company_sought_for}})
        length = len(list(companies.find({"user_id": company_sought_for}))[0]['recieved_from'])
        await bot.send_message(company_sought_for,f'Вам отправили {length} запрос', reply_markup=markup4)
        await state.finish()
        await poisk_company(message, state)
    elif message.text.lower() == "репорт":
        await Report.reporting.set()
        async with state.proxy() as data:
            data['r_id'] = caller_id
        await bot.send_message(caller_id,f'Опишите ситуацию или же напишите /cancel')
    elif message.text.lower() == "главное меню":
        await state.finish()
        button11 = KeyboardButton('Обновить профиль')
        button22 = KeyboardButton("Поиск")
        # Сюда ответ пользователю  !!!!!!!!!!!!!!!!
    else:
        users.update_one({'user_id': caller_id}, {'$push': {'companies': company_sought_for}})
        await state.finish()
        await poisk_company(message, state)


async def poisk(message: types.Message, state: FSMContext):
    id_from_func_caller = str(message.chat.id)
    data = list(users.find({"user_id": str(message.chat.id)}))[0]
    age = data['age']
    city = data['location']
    key_words = [x.lower() for x in data['key_words'].split(",")]
    col = 0
    gender = data['gender']
    searching_gender = data['search_gender']
    geolocator = Nominatim(user_agent="geoapiExercises")
    button1 = KeyboardButton("👍")
    button2 = KeyboardButton("👎")
    button3 = KeyboardButton("Репорт")
    button4 = KeyboardButton("Главное меню")
    if not city.isalpha():
        city = str(geolocator.reverse(city)).split(',')[0]
    markup4 = ReplyKeyboardMarkup(resize_keyboard=True).row(button1, button2, button3, button4)
    for user in users.find({"user_id":{"$ne":id_from_func_caller}}):
        col += 1 
        sought_for = user['user_id']
        
        if sought_for not in data['send_to']:
            if searching_gender == "Все равно":
                searching_gender2 = user['search_gender']
                if searching_gender2 == gender or searching_gender2 == 'Все равно':
                    if abs(int(user['age'])) - int(age) <= 2:
                        
                        city2 = user['location']
                        try:
                            city2 = str(geolocator.reverse(city2)).split(",")[0]
                        except:
                            pass
                        if fuzz.ratio(city, city2) > 60:
                            key_words2 = [x.lower() for x in user['key_words'].split(",")]
                            result=list(set(key_words) & set(key_words2))
                            if result:
                                #print(88888)
                                await state.update_data(caller_id=id_from_func_caller, sought_for=sought_for)
                                #print(99)
                                await Is_liked.liked.set()
                                #print(2349182374923)
                                await bot.send_photo(chat_id=message.chat.id, photo="AgACAgIAAxkBAAII8GI7cbCOcRdlVmNxakP9ehghJD8kAAJevjEbK2zYSZHMQAouYrN1AQADAgADeQADIwQ", caption=f"{user['last_name']} {user['name']}, {user['age']}, {city2}\n\n {user['about_me']}", reply_markup=markup4) 
                                break



            elif searching_gender == "Парень" or "Девушка":
                gender2 = user['gender']
                searching_gender2 = user['search_gender']
                if searching_gender == gender2 and searching_gender2 == gender or searching_gender2 == "Все равно" and searching_gender == gender2:
                    if abs(int(user['age'])) - int(age) <= 2:
                        city2 = user['location']
                        print(city)
                        print(city2)
                        try:
                            city2 = str(geolocator.reverse(city2)).split(",")[0]
                        except:
                            pass
                        if fuzz.ratio(city, city2) > 60:
                            key_words2 = [x.lower() for x in user['key_words'].split(",")]
                            result=list(set(key_words) & set(key_words2))
                            if result:
                                await state.update_data(caller_id=id_from_func_caller, sought_for=sought_for)
                                await Is_liked.liked.set()
                                await bot.send_photo(chat_id=message.chat.id, photo="AgACAgIAAxkBAAII8GI7cbCOcRdlVmNxakP9ehghJD8kAAJevjEbK2zYSZHMQAouYrN1AQADAgADeQADIwQ", caption=f"{user['last_name']} {user['name']},{user['age']}, {city2}\n\n {user['about_me']}", reply_markup=markup4) 
                                break
    #print(col)

@dp.message_handler(state=Is_liked.liked)
async def process_like(message: types.Message, state: FSMContext):
    button1 = KeyboardButton("Посмотреть")
    markup4 = ReplyKeyboardMarkup(resize_keyboard=True).row(button1)
    async with state.proxy() as dat:
        id_from_func_caller = dat['caller_id']
        sought_for = dat['sought_for']
        #state = dat['state']
    data = list(users.find({"user_id": sought_for}))[0] 
    if message.text == "👍":
        users.update_one({'user_id': id_from_func_caller}, {'$push': {'send_to': sought_for}})
        users.update_one({'user_id': sought_for}, {'$push': {'recieved_from': id_from_func_caller}})
        length = len(list(users.find({"user_id": sought_for}))[0]['recieved_from'])
        state = dp.current_state(chat=message.chat.id, user=message.from_user.id)
        await bot.send_message(sought_for,f'Вам отправили {length} запрос', reply_markup=markup4)
        await state.finish()
        await poisk(message, state)
    elif message.text.lower() == "репорт":
        await Report.reporting.set()
        async with state.proxy() as data:
            data['r_id'] = sought_for
        await bot.send_message(message.chat.id,f'Опишите ситуацию или же напишите /cancel', reply_markup=markup4)
    elif message.text.lower() == "главное меню":
        await state.finish()
        button11 = KeyboardButton('Обновить профиль')
        button22 = KeyboardButton("Поиск")
        #сюда ответ пользователю !!!!!!!!!!!!!!!!!!!!
    elif message.text == "👎":
        users.update_one({'user_id': id_from_func_caller}, {'$push': {'send_to': sought_for}})
        await state.finish()
        await poisk(message, state)
    else:
        await state.finish()
        await poisk(message, state)


@dp.message_handler(lambda message: message.text.lower() == 'посмотреть')
async def to_like(message: types.Message, state: FSMContext):
    button11 = KeyboardButton('Обновить профиль')
    button22 = KeyboardButton("Поиск")
    button32 = KeyboardButton("Настройки")
    markup4 = ReplyKeyboardMarkup(resize_keyboard=True).row(button11, button22, button32)
    button1 = KeyboardButton("👍")
    button2 = KeyboardButton("👎")
    button3 = KeyboardButton("Репорт")
    markup3 = ReplyKeyboardMarkup(resize_keyboard=True).row(button1, button2, button3)
    data = list(users.find({"user_id": str(message.chat.id)}))[0]

    if list(users.find({"user_id": str(message.chat.id)}))[0]['right_now']:
        data = list(users.find({"user_id": str(message.chat.id)}))[0]
        try:
            recieved_from = data['recieved_from'][-1]
            profile = list(users.find({"user_id": str(recieved_from)}))[0]
            geolocator = Nominatim(user_agent="geoapiExercises")
            city = profile['location']
            try:
                 city = str(geolocator.reverse(city)).split(",")[0]
            except Exception as e:
                print(e)
                
            users.update_one({'user_id': str(message.chat.id)}, {'$pull': {'recieved_from': recieved_from}})
            await state.update_data(name=profile['name'], recieved_from=recieved_from)
            await for_like.like.set()
            await bot.send_photo(chat_id=message.chat.id, photo=profile['photo'], caption=f"*{profile['last_name']} {profile['name']}*,{profile['age']}, {city}\n\n {profile['about_me']}", reply_markup=markup3, parse_mode=ParseMode.MARKDOWN)         
        except Exception as e:
            await bot.send_message(message.chat.id,f'Список single пустой Нажмите поиск чтобы найти людей. Так же попробуйте сменить страницу и прописать Посмотреть', reply_markup=markup4)
    elif not list(users.find({"user_id": str(message.chat.id)}))[0]['right_now']:
        try:
            data = list(companies.find({"user_id": str(message.chat.id)}))[0]
            recieved_from = data['recieved_from'][-1]
            profile = list(users.find({"user_id": str(recieved_from)}))[0]
            geolocator = Nominatim(user_agent="geoapiExercises")
            city = profile['location']
            try:
                city = str(geolocator.reverse(city)).split(",")[0]
            except Exception as e:
                print(e)        
            companies.update_one({'user_id': str(message.chat.id)}, {'$pull': {'recieved_from': recieved_from}})
            await state.update_data(name=profile['name'], recieved_from=recieved_from)
            await for_like.like.set()
            await bot.send_photo(chat_id=message.chat.id, photo=profile['photo'], caption=f"*{profile['last_name']} {profile['name']}*,{profile['age']}, {city}\n\n {profile['about_me']}", reply_markup=markup3, parse_mode=ParseMode.MARKDOWN)         
        except:
            await bot.send_message(message.chat.id,f'Список company пустой Нажмите поиск чтобы найти людей \n поменяйте страницу чтобы проверить есть новые заявки', reply_markup=markup4)

    else:
        return await message.reply("Зарегистрируйтесь")



@dp.message_handler(state=for_like.like)
async def process_like(message: types.Message, state: FSMContext):
    markup4 = types.ReplyKeyboardRemove()
    async with state.proxy() as data:
        name = data['name']
        recieved_from = data['recieved_from']
    if message.text == "👍":
        await bot.send_message(message.chat.id,f'<a href="tg://openmessage?user_id={recieved_from}">{name}</a>', parse_mode=ParseMode.HTML, reply_markup=markup4)
        await state.finish()
        state = dp.current_state(chat=message.chat.id, user=message.from_user.id)
        await to_like(message, state)
    elif message.text.lower() == "репорт":
        await state.update_data(r_id=recieved_from)
        await Report.reporting.set()
        await bot.send_message(message.chat.id,f'Опишите ситуацию или же напишите /cancel')
    else:
        await state.finish()
        await to_like(message)

@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await message.reply('Ок')

@dp.message_handler(state=Report.reporting)
async def for_report(message: types.Message, state: FSMContext):
    button11 = KeyboardButton('Обновить профиль')
    button22 = KeyboardButton("Поиск")
    markup4 = ReplyKeyboardMarkup(resize_keyboard=True).row(button11, button22)
    async with state.proxy() as data:
        r_id = data['r_id']
    await bot.send_message(1639491822, f'Пользователь <a href="tg://openmessage?user_id={message.chat.id}">{message.chat.id}</a>, отправил репорт сообщение {message.text} с жалобой на {r_id}', parse_mode=ParseMode.HTML, reply_markup=markup4)
    await state.finish()
    state = dp.current_state(chat=message.chat.id, user=message.from_user.id)
    await to_like(message, state)




if __name__ == '__main__':
    from handlers import dp
    dp.middleware.setup(CheckBannedUsers())
    executor.start_polling(dp, skip_updates=True)


