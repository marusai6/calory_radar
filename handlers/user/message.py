from aiogram import types, F, Router, Bot
from aiogram.filters import Command
import html
from aiogram.fsm.context import FSMContext
import asyncpg
import configparser
from states.states import User
from aiogram.types import FSInputFile
from keyboards.user.kb import user_menu
import matplotlib.pyplot as plt

config = configparser.ConfigParser()
config.read('./config/config.ini')

user = config['Database']['db_user']
database = config['Database']['db_name']
host = config['Database']['db_host']
port = config['Database']['db_port']
password = None

router = Router()

@router.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext):
    await message.answer(f'👋<b>{html.escape(message.from_user.full_name)},</b> привет!\n\n'
                         f'Я - бот, который поможет тебе рассчитать калорийность твоего блюда,\n'
                        f'а также содержание белков, жиров и углеводов.\n\n\n'
                        f'Введи название блюда')
    await state.set_state(User.dish)

async def get_kbju(dish: str, massa: float):
    connect = await asyncpg.connect(user=user, database=database, host=host, port=port, password=password)
    query_1 = await connect.fetchrow('''select sum(dolya*kkal) as itog_kkal, sum(dolya*protein) as itog_protein, \
                                     sum(dolya*fat) as itog_fat, sum(dolya*carbohydrates) as itog_carb  from food_req \
                                    where rec_name like '%' || $1 || '%';''', dish.capitalize())
    query_2 = await connect.fetchrow('''select photo_path from food_req where rec_name like '%' || $1 || '%' limit 1; ''', \
                                     dish.capitalize())
    await connect.close()
    kalory = round(float(query_1['itog_kkal'])* massa / 100)
    protein = round(float(query_1['itog_protein'])* massa / 100)
    fat = round(float(query_1['itog_fat'])* massa / 100)
    carb = round(float(query_1['itog_carb'])* massa / 100)
    photo = query_2['photo_path']
    return kalory, protein, fat, carb, photo

def diagramma(protein, fat, carb):
    plt.clf()
    labels = ['Белки', 'Жиры', 'Углеводы']
    values = [protein, fat, carb]
    colors = ['plum','bisque','skyblue']
    plt.pie(values, labels=labels, colors=colors, autopct='%1.1f%%')
    plt.axis('equal')
    plt.savefig('./input/diagram.png')

@router.message(User.dish, F.text)  # Обрабатываем только в состоянии dish
async def handle_dish(message: types.Message, state: FSMContext):
    await state.update_data(dish=message.text)  # Сохраняем название блюда
    await message.answer('Введи вес блюда в граммах')
    await state.set_state(User.massa)

@router.message(User.massa, F.text)  # Обрабатываем только в состоянии massa
async def handle_massa(message: types.Message, state: FSMContext, bot: Bot):
    try:
        massa = float(message.text)
        data = await state.get_data()  # Получаем сохраненные данные (включая dish)
        dish = data.get('dish', '')
        
        kalory, protein, fat, carb, photo = await get_kbju(dish, massa)  # Получаем расчет
        photo = FSInputFile(photo)
        await bot.send_photo(
            chat_id = message.chat.id,
            photo = photo,
            caption=f"🍽 Примерное количество калорий для вашего блюда: {kalory}\n🔸Белков {protein} гр\n🔸Жиров {fat} гр\n♦️Углеводов {carb} гр"
        )
        diagramma(protein, fat, carb)
        await bot.send_photo(chat_id=message.chat.id, photo=FSInputFile('./input/diagram.png'))
        await state.clear()  # Очищаем состояние
        await message.answer("Желаете получить расчёт калорий для другого блюда?", reply_markup=user_menu)
    except ValueError:
        await message.answer('Пожалуйста, введите число для веса блюда')
    except TypeError:
        await message.answer('Такого блюда нет в моей базе')

@router.callback_query(F.data == "No")
async def send_value(callback: types.CallbackQuery):
    await callback.answer(
        text="До новых встреч!",
        show_alert=True
    )

@router.callback_query(F.data == "Yes")
async def send_value(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text="Введи название блюда",
        show_alert=True
    )
    await state.set_state(User.dish)