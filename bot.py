import telebot
import re
from datetime import datetime, timedelta
import json
import os
import time
import requests
import ssl
import sys
import signal
from telebot import apihelper
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# ======================== НАСТРОЙКИ ========================
TOKEN = "8698841559:AAFNogpt2Pk7NBYtwGlo0hE2izKKjV7984U"

# ======================== ПРИНУДИТЕЛЬНЫЙ СБРОС ВЕБХУКА ========================
print("🔄 Принудительный сброс вебхука...")
try:
    response = requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook?drop_pending_updates=true", timeout=10)
    print(f"✅ Вебхук сброшен: {response.json()}")
except Exception as e:
    print(f"⚠️ Ошибка сброса вебхука: {e}")

time.sleep(2)

# ======================== ОБХОД БЛОКИРОВОК ========================
ssl._create_default_https_context = ssl._create_unverified_context

MIRROR_URLS = [
    "https://api.telegram.org",
    "https://api.telegram.baby",
    "https://api.telegram.tech",
]

working_mirror = None
for mirror_url in MIRROR_URLS:
    try:
        print(f"🔄 Пробуем зеркало: {mirror_url}")
        test_url = f"{mirror_url}/bot{TOKEN}/getMe"
        session = requests.Session()
        session.verify = False
        response = session.get(test_url, timeout=10, verify=False)
        if response.status_code == 200:
            working_mirror = mirror_url
            print(f"✅ Найдено рабочее зеркало: {mirror_url}")
            break
    except:
        continue

if working_mirror:
    apihelper.API_URL = working_mirror + "/bot{0}/{1}"
else:
    apihelper.API_URL = "https://api.telegram.org/bot{0}/{1}"

apihelper.READ_TIMEOUT = 60
apihelper.CONNECT_TIMEOUT = 60
bot = telebot.TeleBot(TOKEN)

# ======================== СИСТЕМА ОЗНАКОМЛЕНИЯ ========================
user_agreement = {}

def get_agreement_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    btn = KeyboardButton("✅ ОЗНАКОМИЛСЯ")
    markup.add(btn)
    return markup

def get_sections_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = KeyboardButton("📚 РП ТЕРМИНЫ")
    btn2 = KeyboardButton("⚔️ КАПТ")
    btn3 = KeyboardButton("🏰 ВЧ")
    btn4 = KeyboardButton("💰 ИНКАССАЦИЯ")
    btn5 = KeyboardButton("👤 ПОХИЩЕНИЕ")
    btn6 = KeyboardButton("🚚 КОНВОЙ")
    btn7 = KeyboardButton("👑 НАКАЗАНИЯ ЛИДЕРАМ")
    btn8 = KeyboardButton("📊 ПРОГРЕССИЯ")
    btn9 = KeyboardButton("ℹ️ ПОМОЩЬ")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9)
    return markup

def remove_keyboard():
    return telebot.types.ReplyKeyboardRemove()

# ======================== ЗАГРУЗКА ПРАВИЛ ========================
def load_rules():
    rules = {}
    base_folder = os.getcwd()
    for filename in os.listdir(base_folder):
        if filename.endswith('.txt') and filename != 'bot_stats.json':
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    rules[filename] = f.read()
                print(f"✅ Загружен: {filename}")
            except:
                pass
    return rules

print("📚 Загрузка файлов...")
RULES = load_rules()
print(f"✅ Всего загружено: {len(RULES)} файлов")

# ======================== СТАТИСТИКА ========================
stats_file = 'bot_stats.json'

def load_stats():
    if os.path.exists(stats_file):
        try:
            with open(stats_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"daily": {}, "total_users": []}
    return {"daily": {}, "total_users": []}

def save_stats(stats):
    try:
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
    except:
        pass

stats = load_stats()
user_ids = set(stats.get("total_users", []))

def update_stats(user_id):
    today = datetime.now().strftime("%Y-%m-%d")
    if today not in stats["daily"]:
        stats["daily"][today] = 0
    stats["daily"][today] += 1
    if user_id not in user_ids:
        user_ids.add(user_id)
        stats["total_users"] = list(user_ids)
    save_stats(stats)

# ======================== РП ТЕРМИНЫ ========================
RP_TERMS = {
    'дм': "📚 <b>ДМ (Deathmatch)</b> — Убийство без причины.",
    'дб': "📚 <b>ДБ (DriveBy)</b> — Убийство с машины (или машиной).",
    'ск': "📚 <b>СК (Spawn Kill)</b> — Убийство при появлении персонажа.",
    'тк': "📚 <b>ТК (TeamKill)</b> — Убийство своих союзников.",
    'рп': "📚 <b>РП (RolePlay)</b> — Игра по ролям.",
    'мг': "📚 <b>МГ (MetaGaming)</b> — Использование информации из реального мира.",
    'гм': "📚 <b>ГМ (GodMode)</b> — становление персонажа неуязвимым.",
    'пг': "📚 <b>ПГ (PowerGaming)</b> — Изображение себя как героя.",
    'рк': "📚 <b>РК (RevengeKill)</b> — Возвращение на место смерти.",
    'бх': "📚 <b>БХ (BunnyHop)</b> — Нон-РП бег с прыжками.",
    'ук': "📚 <b>УК (Уголовный Кодекс)</b> — Кодекс законов.",
    'ак': "📚 <b>АК (Академический Кодекс)</b> — Кодекс для учреждений.",
    'зз': "📚 <b>ЗЗ (Зеленая Зона)</b> — Общественные места без агрессии.",
    'фр': "📚 <b>ФР (FastReloading)</b> — Баг с быстрой перезарядкой.",
    'фм': "📚 <b>ФМ (FastMoving)</b> — Баг с быстрым перемещением.",
    'фф': "📚 <b>ФФ (FriendlyFire)</b> — Стрельба по своим.",
    'цк': "📚 <b>ЦК (CharacterKill)</b> — Убийство персонажа (запрещено).",
    'урп': "📚 <b>УРП (UnRolePlay)</b> — Уход от РП.",
    'тдм': "📚 <b>ТДМ (Team DeathMatch)</b> — Командные убийства.",
    'мдм': "📚 <b>МДМ (Mass DeathMatch)</b> — Массовые убийства.",
    'орп': "📚 <b>ОРП (OffRolePlay)</b> — Уход от РП.",
    'епп': "📚 <b>ЕПП (Exploiting Pathing)</b> — Езда по полям.",
    'пк': "📚 <b>ПК (PlayerKill)</b> — РП убийство.",
    'фцк': "📚 <b>ФЦК (FractionCharacterKill)</b> — Убийство по фракции.",
    'ooc': "📚 <b>OOC (Out Of Character)</b> — Информация вне игры.",
    'ic': "📚 <b>IC (In Character)</b> — Информация в игре.",
    'все термины': "📚 <b>СПИСОК ВСЕХ РП-ТЕРМИНОВ:</b>\n\n• ДМ — Убийство без причины\n• ДБ — Убийство с машины\n• СК — Убийство при появлении\n• ТК — Убийство своих\n• РП — Игра по ролям\n• МГ — Информация извне\n• ГМ — Неуязвимость\n• ПГ — Геройство\n• РК — Месть\n• БХ — Прыжки\n• УК — Уголовный Кодекс\n• АК — Академический Кодекс\n• ЗЗ — Зеленая Зона\n• ФР — Баг перезарядки\n• ФМ — Баг движения\n• ФФ — Огонь по своим\n• ЦК — Убийство персонажа\n• УРП — Уход от РП\n• ТДМ — Командные убийства\n• МДМ — Массовые убийства\n• ОРП — Уход от РП\n• ЕПП — Езда по полям\n• ПК — РП убийство\n• ФЦК — Убийство по фракции\n• OOC — Вне игры\n• IC — В игре"
}

# ======================== ПРОГРЕССИЯ ========================
PROGRESS_ANSWERS = {
    '1 уровень': "📊 <b>1 УРОВЕНЬ ПРОГРЕССИИ ОПГ:</b>\n\n🚗 Автопарк: Mercedes CLS63 AMGs 2019, Mercedes G63, Maybach x222, Mercedes S600\n🚘 Машин: 12\n📦 Склад: 100 предметов\n💰 Зарплата: 50 руб за территорию\n🏆 Территорий: 3",
    '2 уровень': "📊 <b>2 УРОВЕНЬ ПРОГРЕССИИ ОПГ:</b>\n\n🚗 Автопарк: + Mercedes-Benz V-класса\n🚘 Машин: 15\n📦 Склад: 150 предметов\n✨ Бонус: +100 материалов/час\n💰 Зарплата: 100 руб +10%\n🏆 Территорий: 15",
    '3 уровень': "📊 <b>3 УРОВЕНЬ ПРОГРЕССИИ ОПГ:</b>\n\n🚗 Автопарк: + BMW M5 Ф90, Lexus XL570\n🚘 Машин: 17\n📦 Склад: 170 предметов\n✨ Бонус: +300 материалов/час\n💰 Зарплата: 150 руб +15%\n🏆 Территорий: 30",
    '4 уровень': "📊 <b>4 УРОВЕНЬ ПРОГРЕССИИ ОПГ:</b>\n\n🚗 Автопарк: + Rolls-Royce Cullinan\n🚘 Машин: 20\n📦 Склад: 200 предметов\n✨ Бонус: +500 материалов/час\n💰 Зарплата: 200 руб +20%\n🏆 Территорий: 50",
    'все уровни': "📊 <b>ВСЕ УРОВНИ ПРОГРЕССИИ ОПГ:</b>\n\n1 уровень: 3 территории, 12 машин\n2 уровень: 15 территорий, 15 машин, +100 мат/час\n3 уровень: 30 территорий, 17 машин, +300 мат/час\n4 уровень: 50 территорий, 20 машин, +500 мат/час",
}

# ======================== КАПТ (НОВЫЕ ВОПРОСЫ) ========================
CAPT_ANSWERS = {
    'территории эдово лыткарино': "📍 <b>Территории:</b>\n\nЭдово - 45 территорий\nЛыткарино - 33 территории\nВсего - 78 территорий",
    
    'цвета опг': "🎨 <b>Цвета ОПГ:</b>\n\nТамбов - Фиолетовый\nОффники - Зелёный\nКавказ - Бирюзовый",
    
    'время забития': "⏰ <b>Время забития в войну за территорию:</b>\n\nВ нечётное время каждые 2 часа по московскому времени.\n\n📅 Будние дни (13:00 до 21:05):\n13:00 | 15:00 | 17:00 | 19:00 | 21:00\n\n📅 Выходные дни (11:00 до 21:05):\n11:00 | 13:00 | 15:00 | 17:00 | 19:00 | 21:00",
    
    'атакующая сторона': "⚔️ <b>Атакующая сторона:</b>\n\nСторона, первая забившая войну за территорию.",
    
    'обороняющаяся сторона': "🛡️ <b>Обороняющаяся сторона:</b>\n\nСторона, изначально владеющая территорией, за которую забили войну.",
    
    'длительность боя': "⏱️ <b>Длительность боя:</b>\n\n15 минут",
    
    'длительность подготовки': "⏱️ <b>Длительность подготовки:</b>\n\n10 минут",
    
    'заморозка лидера': "❄️ <b>Заморозка лидера:</b>\n\n1 день",
    
    'дресс код': "👔 <b>Нахождение не по дресс-коду:</b>\n\n❌ ЗАПРЕЩЕНО\nНаказание: Тюрьма 10 минут",
    
    'фуллка': "🏆 <b>Фуллка:</b>\n\n72 территории",
    
    'афк': "💤 <b>АФК на капте:</b>\n\n✅ Разрешено не более 15 секунд\n❌ Если больше 15 секунд — Кик с сервера",
    
    'сбивание анимации': "🎬 <b>Сбивание анимации (наркотики/аптечки/еда):</b>\n\n❌ ЗАПРЕЩЕНО\nНаказание: Тюрьма 20 минут",
    
    'оффтоп': "💬 <b>Оффтоп на капте:</b>\n\n❌ ЗАПРЕЩЕН\nНаказание: Мут 20 минут",
    
    'огнетушитель баллончик': "🧯 <b>Использование огнетушителя или баллончика:</b>\n\n❌ ЗАПРЕЩЕНО\nНаказание: Тюрьма 60 минут",
    
    'без формы': "👕 <b>Нахождение без формы:</b>\n\n❌ ЗАПРЕЩЕНО\nНаказание: Тюрьма 10 минут",
    
    'антикапт': "🛑 <b>Антикапт:</b>\n\n❌ ЗАПРЕЩЕНО\nНаказание: Тюрьма 60 минут, при повторе — варн",
    
    'пинг': "📶 <b>Максимальный пинг:</b>\n\n200\nЕсли выше — кик",
    
    'стрельба с аптечкой': "💊 <b>Использование аптечки/баллончика во время стрельбы:</b>\n\n❌ ЗАПРЕЩЕНО\nНаказание: Тюрьма 10 минут",
    
    'стрельба в подготовке': "🔫 <b>Стрельба во время подготовки:</b>\n\n❌ ЗАПРЕЩЕНО\nНаказание: Тюрьма 60 минут",
    
    'софт': "💻 <b>Использование СОФТ (стороннего ПО):</b>\n\n❌ ЗАПРЕЩЕНО\nНаказание: Бан аккаунта + ЧСП проекта",
    
    'интерьер': "🏠 <b>Заход в интерьер:</b>\n\n❌ ЗАПРЕЩЕНО\nНаказание: Тюрьма 10 минут",
    
    'маска': "🎭 <b>Маска на капте:</b>\n\n❌ ЗАПРЕЩЕНО\nНаказание: Тюрьма 10 минут",
    
    'стрельба по неучастникам': "🎯 <b>Стрельба/убийство игроков, не относящихся к капту:</b>\n\n❌ ЗАПРЕЩЕНО\nНаказание: Тюрьма 90 минут",
    
    'провокация': "😡 <b>Провокация вражеской ОПГ:</b>\n\n❌ ЗАПРЕЩЕНО\nНаказание: Мут 10 минут",
    
    'багоюз': "🐛 <b>Багоюз:</b>\n\n❌ ЗАПРЕЩЕН\nНаказание: Тюрьма 60 минут\n\n✅ Исключение: анимации стрельбы (+с, отводы и т.п.)",
    
    'высотки': "🏢 <b>Занятие крыш высоких зданий:</b>\n\n❌ ЗАПРЕЩЕНО (с помощью вертолёта, бага)\nНаказание: Варн",
    
    'сторонние игроки': "👥 <b>Вмешательство сторонних игроков:</b>\n\n❌ ЗАПРЕЩЕНО\nНаказание: Варн",
    
    'ск': "🔫 <b>СК (Spawn Kill):</b>\n\n❌ ЗАПРЕЩЕНО\nНаказание: Тюрьма 60 минут",
    
    'неразрешенное оружие': "🔫 <b>Использование неразрешенного оружия:</b>\n\n❌ ЗАПРЕЩЕНО\nНаказание: Тюрьма 10 минут\n\n✅ Исключение: баллончик и огнетушитель — тюрьма 60 минут",
    
    'крыши тюнинг': "🏢 <b>Забирание на крыши при помощи тюнинга авто, джетпака:</b>\n\n❌ ЗАПРЕЩЕНО\nНаказание: Тюрьма 20 минут",
    
    'выход за территорию': "🚪 <b>Выход за территорию:</b>\n\n❌ ЗАПРЕЩЕНО\nНаказание: Тюрьма 20 минут",
    
    'красная зона': "🔴 <b>Красная зона:</b>\n\nЗона вне проведения капта. В ней запрещено убивать вражескую ОПГ, а также выезжать в неё.",
    
    'оранжевая зона': "🟠 <b>Оранжевая зона:</b>\n\nПрилегающие территории. Разрешено находиться и перемещаться. Убийства в этой зоне НЕ идут в счетчик.\n\n⚠️ Во время боя запрещено уходить в оранжевую зону, а также наносить урон по тем, кто находится в этой зоне или наносить урон с этой зоны. Наказание: Тюрьма 20 минут.",
    
    'зеленая зона': "🟢 <b>Зелёная зона:</b>\n\nЗона, где расположены территории. Убийства в этой зоне идут в счётчик.",
    
    'накрутка килов': "📊 <b>Накрутка киллов:</b>\n\n❌ ЗАПРЕЩЕНА\nНаказание: Варн",
    
    'цвет ника': "🎨 <b>Смена цвета ника с фракционного:</b>\n\n❌ ЗАПРЕЩЕНО\nНаказание: Кик с сервера",
    
    'афк орп': "💤 <b>Уход в АФК или ОРП:</b>\n\n❌ ЗАПРЕЩЕНО\nНаказание: Тюрьма 10 минут",
    
    'капс флуд': "📢 <b>Капс и флуд:</b>\n\n✅ РАЗРЕШЕН за 15 минут до начала и во время (исключительно по теме войны, 7 рангам и выше, не более 6 строк в минуту)\n\n❌ За несоблюдение: Мут 20 минут",
    
    'пг': "💪 <b>ПГ (PowerGaming):</b>\n\n✅ РАЗРЕШЕН",
    
    'рк': "🔄 <b>РК (RevengeKill):</b>\n\n✅ РАЗРЕШЕН",
    
    'баги стрельбы': "🎯 <b>Баги стрельбы (+с, отводы и т.п.):</b>\n\n✅ РАЗРЕШЕНЫ",
    
    'пдд': "🚗 <b>Нарушение ПДД:</b>\n\n✅ РАЗРЕШЕНО за 5 минут до начала капта и до его окончания",
    
    'минимальное количество': "👥 <b>Минимальное количество человек от одной ОПГ:</b>\n\n10 человек",
    
    'разрешенное оружие': "🔫 <b>РАЗРЕШЕННОЕ ОРУЖИЕ:</b>\n\n• Пистолет Макарова\n• Пистолет с глушителем\n• AK47\n• Дробовик\n• Rifle\n• Бита\n• Кулаки\n• АК74\n• Кастет",
}

# ======================== ВЧ ========================
VCH_ANSWERS = {
    'вч время': "✅ с 8:00 до 22:00",
    'вч без маски': "❌ Тюрьма 30 минут",
    'вч без формы': "❌ Тюрьма 10 минут",
    'вч интерьеры': "❌ Тюрьма 30 минут / Warn",
    'вч аптечки': "❌ Тюрьма 30 минут",
    'вч дм вне': "❌ Тюрьма 90 минут",
    'вч меньше 5': "❌ Тюрьма 30 минут",
    'вч анимации': "❌ Тюрьма 30 минут",
    'вч наркотики': "✅ Разрешено (НЕ в бою)",
    'вч подкуп': "✅ Разрешено",
    'вч убийство': "✅ На территории ВЧ",
    'вч заезд': "✅ Через КПП и дырки",
    'вч минимум': "✅ 5 человек"
}

# ======================== ИНКАССАЦИЯ ========================
INCASS_ANSWERS = {
    'варны': "⚠️ 1. Нет 6+ ранга - Деморган 30/Warn\n2. Перекрытие дороги - Деморган 30/Warn\n3. Бить кулаками - Деморган 60-90/Warn\n4. Меньше 4 человек - Деморган 30/Warn\n5. Нападение в городе - Деморган 60/Warn\n6. Стрельба из окна - Warn",
    'время': "💰 Запрещено с 00:00 до 06:00",
    'место': "📍 Только за чертой города",
    'минимум': "👥 4 человека",
    'маска': "❌ Без маски - Деморган 60-90/Warn",
    'кулаки': "❌ Бить кулаками - Деморган 60-90/Warn",
    'город': "❌ В городе - Деморган 60/Warn",
    'стрельба из окна': "❌ Стрельба из окна - Warn",
    'интерьер': "❌ Заход в интерьер - Деморган 60",
    'ночь': "❌ Ночью - Деморган 60",
    'аптечка': "✅ Под прикрытием или после",
    'транспорт': "✅ Личный/семейный/фракционный"
}

# ======================== ПОХИЩЕНИЕ ========================
KIDNAP_ANSWERS = {
    'время лидеров': "⏰ с 12:00 до 20:00",
    'за раз': "👥 Только 1 человека",
    'гос работники': "👮‍♂️ С промежутком 2 часа",
    'называть похитителей': "❌ ЗАПРЕЩЕНО",
    'афк': "❌ ЗАПРЕЩЕНО - AFK От Смерти",
    'провокация': "❌ ЗАПРЕЩЕНО",
    'лидеров в день': "👑 Максимум 3 раза, 1 лидер - 1 раз",
    'переговоры': "🤝 По 1 человеку от ОПГ и МВД",
    'переговорщикам': "🚫 Маска, огонь",
    'зз': "❌ ЗАПРЕЩЕНО",
    'рп убийство': "❌ ЗАПРЕЩЕНО",
    'убить заложника': "❌ ЗАПРЕЩЕНО после выкупа",
    'что нужно': "🎭 1. План 2. Оружие 3. Маска",
    'выкупы': "💰 Губернатор - 250к, Зам - 100к, Сотрудники - 25к, МВД/ВЧ - 150к/75к/20к, ФСБ - 200к/100к/25к"
}

# ======================== КОНВОЙ ========================
CONVOY_ANSWERS = {
    'дм на шахте': "❌ /jail 90",
    'танк': "❌ /warn",
    'запрещенное место': "❌ /jail 90",
    'помеха армейцам': "❌ ЗАПРЕЩЕНА",
    'убийство опг': "✅ РАЗРЕШЕНО",
    'все правила': "🚚 Только на трассе Арзамас-Южный, одна ОПГ"
}

# ======================== НАКАЗАНИЯ ЛИДЕРАМ ========================
LEADER_ANSWERS = {
    'массовые нарушения': "👑 <b>Массовые нарушения состава (8+ человек):</b>\n\nПредупреждение лидеру",
    'захват в морозе': "👑 <b>Захват территории ОПГ в морозе:</b>\n\nВыговор лидеру",
    '3+ чита': "👑 <b>Больше трех игроков с читами с одной ОПГ:</b>\n\nВыговор лидеру",
    'продажа территорий': "👑 <b>Продажа/покупка/отдача территорий, перемирие с вражеской ОПГ:</b>\n\nВыговор лидеру",
    'не приезд': "👑 <b>Не приезд на войну в город, где закаптили территорию:</b>\n\nПредупреждение лидеру",
    'забитие не по времени': "👑 <b>Забитие войны за территории не по времени (в четные часы):</b>\n\nПредупреждение лидеру",
    'увольнение на капте': "👑 <b>Увольнение/понижение/повышение/прием/выдача выговоров людям на капте:</b>\n\nВыговор лидеру",
    'все наказания': "👑 <b>ВСЕ НАКАЗАНИЯ ЛИДЕРАМ:</b>\n\n• Массовые нарушения (8+ чел) - Предупреждение\n• Захват территории в морозе - Выговор\n• 3+ игроков с читами - Выговор\n• Продажа/покупка/перемирие - Выговор\n• Не приезд на войну - Предупреждение\n• Забитие не по времени - Предупреждение\n• Увольнения на капте - Выговор"
}

# ======================== ПОИСК ОТВЕТА ========================
def find_answer(query):
    q = query.lower().strip()
    
    # РП термины
    for term, answer in RP_TERMS.items():
        if term in q:
            return answer
    
    # Прогрессия
    if '1 уровень' in q:
        return PROGRESS_ANSWERS['1 уровень']
    if '2 уровень' in q:
        return PROGRESS_ANSWERS['2 уровень']
    if '3 уровень' in q:
        return PROGRESS_ANSWERS['3 уровень']
    if '4 уровень' in q:
        return PROGRESS_ANSWERS['4 уровень']
    if 'все уровни' in q:
        return PROGRESS_ANSWERS['все уровни']
    
    # КАПТ (новые вопросы)
    if 'сколько территорий' in q and ('эдово' in q or 'лыткарино' in q):
        return CAPT_ANSWERS['территории эдово лыткарино']
    if 'цвет' in q and 'опг' in q:
        return CAPT_ANSWERS['цвета опг']
    if 'когда можно забивать' in q or 'время забития' in q:
        return CAPT_ANSWERS['время забития']
    if 'атакующая сторона' in q:
        return CAPT_ANSWERS['атакующая сторона']
    if 'обороняющаяся сторона' in q or 'обороняющиеся' in q:
        return CAPT_ANSWERS['обороняющаяся сторона']
    if 'длительность боя' in q or 'сколько минут бой' in q:
        return CAPT_ANSWERS['длительность боя']
    if 'длительность подготовки' in q or 'сколько минут подготовка' in q:
        return CAPT_ANSWERS['длительность подготовки']
    if 'заморозка' in q and 'лидер' in q:
        return CAPT_ANSWERS['заморозка лидера']
    if 'дресс-код' in q or 'не по дресс-коду' in q:
        return CAPT_ANSWERS['дресс код']
    if 'фуллка' in q or 'сколько территорий фуллка' in q:
        return CAPT_ANSWERS['фуллка']
    if 'афк' in q:
        return CAPT_ANSWERS['афк']
    if 'сбивать анимации' in q:
        return CAPT_ANSWERS['сбивание анимации']
    if 'оффтоп' in q:
        return CAPT_ANSWERS['оффтоп']
    if 'огнетушитель' in q or 'баллончик' in q:
        return CAPT_ANSWERS['огнетушитель баллончик']
    if 'без формы' in q:
        return CAPT_ANSWERS['без формы']
    if 'антикапт' in q:
        return CAPT_ANSWERS['антикапт']
    if 'пинг' in q:
        return CAPT_ANSWERS['пинг']
    if 'стрельба' in q and 'аптечка' in q:
        return CAPT_ANSWERS['стрельба с аптечкой']
    if 'стрельба' in q and 'подготовка' in q:
        return CAPT_ANSWERS['стрельба в подготовке']
    if 'софт' in q:
        return CAPT_ANSWERS['софт']
    if 'интерьер' in q:
        return CAPT_ANSWERS['интерьер']
    if 'маска' in q:
        return CAPT_ANSWERS['маска']
    if 'не относятся' in q or 'не участвуют' in q:
        return CAPT_ANSWERS['стрельба по неучастникам']
    if 'провоцировать' in q:
        return CAPT_ANSWERS['провокация']
    if 'багоюз' in q:
        return CAPT_ANSWERS['багоюз']
    if 'крыши' in q and 'вертолёт' in q:
        return CAPT_ANSWERS['высотки']
    if 'сторонние' in q and 'игроки' in q:
        return CAPT_ANSWERS['сторонние игроки']
    if 'ск' in q and 'капт' in q:
        return CAPT_ANSWERS['ск']
    if 'неразрешенное оружие' in q or 'не разрешенное оружие' in q:
        return CAPT_ANSWERS['неразрешенное оружие']
    if 'крыши' in q and 'тюнинг' in q:
        return CAPT_ANSWERS['крыши тюнинг']
    if 'выход за территорию' in q:
        return CAPT_ANSWERS['выход за территорию']
    if 'красная зона' in q:
        return CAPT_ANSWERS['красная зона']
    if 'оранжевая зона' in q:
        return CAPT_ANSWERS['оранжевая зона']
    if 'зеленая зона' in q:
        return CAPT_ANSWERS['зеленая зона']
    if 'накрутка' in q and 'килов' in q:
        return CAPT_ANSWERS['накрутка килов']
    if 'цвет ника' in q:
        return CAPT_ANSWERS['цвет ника']
    if 'афк' in q and 'орп' in q:
        return CAPT_ANSWERS['афк орп']
    if 'капс' in q or 'флуд' in q:
        return CAPT_ANSWERS['капс флуд']
    if 'пг' in q:
        return CAPT_ANSWERS['пг']
    if 'рк' in q:
        return CAPT_ANSWERS['рк']
    if 'баги стрельбы' in q:
        return CAPT_ANSWERS['баги стрельбы']
    if 'пдд' in q:
        return CAPT_ANSWERS['пдд']
    if 'минимальное количество' in q or 'сколько человек' in q:
        return CAPT_ANSWERS['минимальное количество']
    if 'оружие' in q:
        return CAPT_ANSWERS['разрешенное оружие']
    
    # ВЧ
    if 'вч' in q and ('со скольки' in q or 'до скольки' in q):
        return VCH_ANSWERS['вч время']
    if 'вч' in q and 'маск' in q:
        return VCH_ANSWERS['вч без маски']
    if 'вч' in q and 'форм' in q:
        return VCH_ANSWERS['вч без формы']
    if 'вч' in q and 'интерьер' in q:
        return VCH_ANSWERS['вч интерьеры']
    if 'вч' in q and 'аптечк' in q:
        return VCH_ANSWERS['вч аптечки']
    if 'вч' in q and 'дм' in q:
        return VCH_ANSWERS['вч дм вне']
    if 'вч' in q and 'минимум' in q:
        return VCH_ANSWERS['вч минимум']
    if 'вч' in q and 'сбив' in q:
        return VCH_ANSWERS['вч анимации']
    if 'вч' in q and 'подкуп' in q:
        return VCH_ANSWERS['вч подкуп']
    if 'вч' in q and 'убива' in q:
        return VCH_ANSWERS['вч убийство']
    if 'вч' in q and 'наркотик' in q:
        return VCH_ANSWERS['вч наркотики']
    
    # Инкассация
    if 'инкассац' in q or 'инкосац' in q:
        if 'варн' in q:
            return INCASS_ANSWERS['варны']
        if 'со скольки' in q or 'до скольки' in q:
            return INCASS_ANSWERS['время']
        if 'где' in q:
            return INCASS_ANSWERS['место']
        if 'сколько' in q:
            return INCASS_ANSWERS['минимум']
        if 'маск' in q:
            return INCASS_ANSWERS['маска']
        if 'кулак' in q:
            return INCASS_ANSWERS['кулаки']
        if 'город' in q:
            return INCASS_ANSWERS['город']
        if 'стрельб' in q and 'окн' in q:
            return INCASS_ANSWERS['стрельба из окна']
        if 'интерьер' in q:
            return INCASS_ANSWERS['интерьер']
        if 'ноч' in q:
            return INCASS_ANSWERS['ночь']
        if 'аптечк' in q:
            return INCASS_ANSWERS['аптечка']
        if 'транспорт' in q:
            return INCASS_ANSWERS['транспорт']
    
    # Похищение
    if 'похищ' in q:
        if 'лидер' in q and ('со скольки' in q or 'до скольки' in q):
            return KIDNAP_ANSWERS['время лидеров']
        if 'за раз' in q:
            return KIDNAP_ANSWERS['за раз']
        if 'гос' in q and 'работник' in q:
            return KIDNAP_ANSWERS['гос работники']
        if 'называть' in q:
            return KIDNAP_ANSWERS['называть похитителей']
        if 'афк' in q:
            return KIDNAP_ANSWERS['афк']
        if 'провоцир' in q:
            return KIDNAP_ANSWERS['провокация']
        if 'сколько' in q and 'лидер' in q and 'день' in q:
            return KIDNAP_ANSWERS['лидеров в день']
        if 'переговор' in q and 'сколько' in q:
            return KIDNAP_ANSWERS['переговоры']
        if 'переговорщ' in q and 'запрещ' in q:
            return KIDNAP_ANSWERS['переговорщикам']
        if 'зз' in q:
            return KIDNAP_ANSWERS['зз']
        if 'рп убийств' in q:
            return KIDNAP_ANSWERS['рп убийство']
        if 'убить' in q and 'заложник' in q:
            return KIDNAP_ANSWERS['убить заложника']
        if 'что нужно' in q:
            return KIDNAP_ANSWERS['что нужно']
        if 'выкуп' in q:
            return KIDNAP_ANSWERS['выкупы']
    
    # Конвой
    if 'конвой' in q:
        if 'дм' in q and 'шахт' in q:
            return CONVOY_ANSWERS['дм на шахте']
        if 'танк' in q:
            return CONVOY_ANSWERS['танк']
        if 'запрещенн' in q:
            return CONVOY_ANSWERS['запрещенное место']
        if 'помех' in q:
            return CONVOY_ANSWERS['помеха армейцам']
        if 'убивать' in q:
            return CONVOY_ANSWERS['убийство опг']
        if 'все правила' in q:
            return CONVOY_ANSWERS['все правила']
    
    # Наказания лидерам
    if 'лидер' in q:
        if 'массов' in q:
            return LEADER_ANSWERS['массовые нарушения']
        if 'мороз' in q:
            return LEADER_ANSWERS['захват в морозе']
        if '3+' in q or 'трех' in q:
            return LEADER_ANSWERS['3+ чита']
        if 'продаж' in q:
            return LEADER_ANSWERS['продажа территорий']
        if 'не приезд' in q:
            return LEADER_ANSWERS['не приезд']
        if 'не по времени' in q:
            return LEADER_ANSWERS['забитие не по времени']
        if 'увольн' in q:
            return LEADER_ANSWERS['увольнение на капте']
        if 'все наказания' in q:
            return LEADER_ANSWERS['все наказания']
    
    # Файлы
    for filename, content in RULES.items():
        if filename.lower().replace('.txt', '') in q:
            return f"📄 {filename}\n\n{content}"
    
    return None

# ======================== КЛАВИАТУРЫ ========================
def get_rp_terms_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    terms = ["ДМ", "ДБ", "СК", "ТК", "РП", "МГ", "ГМ", "ПГ", "РК", "БХ", "УК", "АК", "ЗЗ", "ФР", "ФМ", "ФФ", "ЦК", "УРП", "ТДМ", "МДМ", "ОРП", "ЕПП", "ПК", "ФЦК", "OOC", "IC", "все термины", "🔙 НАЗАД"]
    for t in terms:
        markup.add(KeyboardButton(t))
    return markup

def get_capt_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    questions = [
        "📍 Сколько территорий в Эдово и Лыткарино?",
        "🎨 Какого цвета каждое ОПГ?",
        "⏰ Когда можно забивать в войну за территорию?",
        "⚔️ Кто такая атакующая сторона?",
        "🛡️ Кто такая обороняющаяся сторона?",
        "⏱️ Сколько минут длится война за территорию?",
        "⏱️ Сколько минут длится подготовка?",
        "❄️ На сколько дней лидер имеет право брать заморозку?",
        "👔 Разрешено ли на капте не по дресс-коду?",
        "🏆 Сколько территорий считается фуллкой?",
        "💤 Разрешено ли АФК на капте?",
        "🎬 Разрешено ли сбивать анимации?",
        "💬 Разрешен ли оффтоп?",
        "🧯 Разрешено ли использовать огнетушитель или баллончик?",
        "👕 Можно ли нарушать дресс-код или находиться без формы?",
        "🛑 Разрешен ли антикапт?",
        "📶 Максимальный разрешенный пинг?",
        "💊 Разрешено ли во время стрельбы использовать аптечку?",
        "🔫 Разрешено ли стрелять во время подготовки?",
        "💻 Разрешено ли использовать СОФТ?",
        "🏠 Разрешено ли заходить в интерьер?",
        "🎭 Разрешено ли надевать маску?",
        "🎯 Разрешено ли стрелять/убивать игроков, которые не относятся к капту?",
        "😡 Можно ли провоцировать вражескую ОПГ?",
        "🐛 Разрешен ли багаюз?",
        "🏢 Разрешено ли занимать крыши высоких зданий с помощью вертолёта?",
        "👥 Разрешено ли вмешиваться в капт сторонним игрокам?",
        "🔫 Разрешен ли СК?",
        "🔫 Разрешено ли использовать не разрешенное оружие?",
        "🏢 Разрешено ли забираться на крыши при помощи тюнинга авто, джетпака?",
        "🚪 Разрешено ли выходить за территорию?",
        "🔴 Что такое красная зона?",
        "🟠 Что такое оранжевая зона?",
        "🟢 Что такое зелёная зона?",
        "📊 Разрешено ли накручивать киллы?",
        "🎨 Разрешено ли менять цвет ника с фракционного?",
        "💤 Разрешено ли уходить в АФК или делать ОРП?",
        "📢 Разрешен ли капс и флуд?",
        "💪 Разрешен ли ПГ?",
        "🔄 Разрешен ли РК?",
        "🎯 Разрешено ли использовать баги стрельбы (+с, отводы)?",
        "🚗 Разрешено ли нарушать ПДД?",
        "👥 Минимальное количество человек от одной ОПГ?",
        "🔫 Какое оружие разрешено?",
        "🔙 НАЗАД"
    ]
    for q in questions:
        markup.add(KeyboardButton(q))
    return markup

def get_vch_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    questions = ["⏰ Со скольки до скольки можно нападать?", "🎭 Можно ли быть без маски?", "👔 Можно ли без формы?", "🏠 Можно ли заходить в интерьеры?", "💊 Можно ли использовать аптечки?", "🔫 Можно ли ДМ вне территории?", "👥 Сколько нужно человек минимум?", "🎬 Можно ли сбивать анимации?", "💰 Можно ли подкупать?", "⚔️ Можно ли убивать военнослужащих?", "🚗 Куда можно заезжать?", "🔙 НАЗАД"]
    for q in questions:
        markup.add(KeyboardButton(q))
    return markup

def get_incass_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    questions = ["⚠️ Варны в инкассации", "⏰ Со скольки до скольки нельзя нападать?", "📍 Где можно нападать?", "👥 Сколько нужно человек?", "🎭 Можно ли без маски?", "👊 Можно ли бить кулаками?", "🏙️ Можно ли нападать в городе?", "🚗 Можно ли стрелять из окна?", "🏪 Можно ли заходить в интерьер?", "🌙 Можно ли нападать ночью?", "💊 Можно ли использовать аптечку?", "🚗 Какой транспорт можно использовать?", "🔙 НАЗАД"]
    for q in questions:
        markup.add(KeyboardButton(q))
    return markup

def get_kidnap_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    questions = ["👑 Со скольки до скольки можно похищать лидеров?", "👥 Сколько можно похищать за раз?", "👮‍♂️ Когда можно похищать гос. работников?", "📛 Можно ли называть похитителей по имени?", "💤 Можно ли уходить в AFK?", "😠 Можно ли провоцировать?", "👑 Сколько лидеров можно в день?", "🤝 Сколько человек для переговоров?", "🚫 Что запрещено переговорщикам?", "🌳 Можно ли похищать в ЗЗ?", "⚰️ Можно ли РП убийство?", "💀 Можно ли убить заложника?", "🎭 Что нужно похитителю?", "💰 Суммы выкупов", "🔙 НАЗАД"]
    for q in questions:
        markup.add(KeyboardButton(q))
    return markup

def get_convoy_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    questions = ["⛏️ Можно ли ДМить на шахте?", "🚜 Можно ли брать танк?", "🚫 Можно ли нападать в запрещенных местах?", "🚚 Можно ли мешать армейцам?", "🤝 Можно ли ОПГ убивать друг друга?", "📋 Все правила конвоя", "🔙 НАЗАД"]
    for q in questions:
        markup.add(KeyboardButton(q))
    return markup

def get_leader_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    questions = ["👑 Что даётся за массовые нарушения?", "❄️ Что даётся за захват в морозе?", "💻 Что даётся за 3+ чита?", "💰 Что даётся за продажу территорий?", "🚫 Что даётся за не приезд?", "⏰ Что даётся за забитие не по времени?", "📝 Что даётся за увольнение на капте?", "📋 Все наказания лидерам", "🔙 НАЗАД"]
    for q in questions:
        markup.add(KeyboardButton(q))
    return markup

def get_progress_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    questions = ["1️⃣ 1 уровень прогрессии", "2️⃣ 2 уровень прогрессии", "3️⃣ 3 уровень прогрессии", "4️⃣ 4 уровень прогрессии", "📊 Все уровни", "🔙 НАЗАД"]
    for q in questions:
        markup.add(KeyboardButton(q))
    return markup

# ======================== ОБРАБОТЧИКИ ========================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    update_stats(message.from_user.id)
    user_id = message.from_user.id
    if user_id not in user_agreement:
        user_agreement[user_id] = 0
    
    welcome_text = """
👋 <b>Привет! Я бот для подготовки к обзвонам на Ghetto.</b>

📌 <b>Перед использованием нажмите кнопку "ОЗНАКОМИЛСЯ" 3 раза</b>

👇 <b>Нажмите кнопку 3 раза для доступа</b>
    """
    bot.send_message(message.chat.id, welcome_text, parse_mode='HTML', reply_markup=get_agreement_keyboard())

@bot.message_handler(func=lambda message: message.text == "✅ ОЗНАКОМИЛСЯ")
def handle_agreement(message):
    user_id = message.from_user.id
    if user_id not in user_agreement:
        user_agreement[user_id] = 0
    user_agreement[user_id] += 1
    clicks = user_agreement[user_id]
    
    if clicks >= 3:
        user_agreement[user_id] = 3
        welcome_text = f"""
✅ <b>Спасибо! Вы ознакомились с правилами.</b>

📚 <b>Загружено:</b> {len(RULES)} файлов + полная база знаний
✅ <b>Выберите раздел для вопросов:</b>

📚 <b>РП ТЕРМИНЫ</b> - значения всех терминов
⚔️ <b>КАПТ</b> - война за территории
🏰 <b>ВЧ</b> - военная часть
💰 <b>ИНКАССАЦИЯ</b> - ограбление инкассации
👤 <b>ПОХИЩЕНИЕ</b> - правила похищения
🚚 <b>КОНВОЙ</b> - военный конвой
👑 <b>НАКАЗАНИЯ ЛИДЕРАМ</b> - наказания лидерам
📊 <b>ПРОГРЕССИЯ</b> - уровни ОПГ
ℹ️ <b>ПОМОЩЬ</b> - помощь по боту

📊 <b>Статистика:</b> /stats
        """
        bot.send_message(message.chat.id, welcome_text, parse_mode='HTML', reply_markup=get_sections_keyboard())
    else:
        remaining = 3 - clicks
        bot.send_message(message.chat.id, f"⚠️ <b>Осталось нажатий: {remaining}</b>", parse_mode='HTML', reply_markup=get_agreement_keyboard())

@bot.message_handler(func=lambda message: message.text == "🔙 НАЗАД")
def go_back(message):
    welcome_text = """
📚 <b>Выберите раздел для вопросов:</b>

📚 <b>РП ТЕРМИНЫ</b> - значения всех терминов
⚔️ <b>КАПТ</b> - война за территории
🏰 <b>ВЧ</b> - военная часть
💰 <b>ИНКАССАЦИЯ</b> - ограбление инкассации
👤 <b>ПОХИЩЕНИЕ</b> - правила похищения
🚚 <b>КОНВОЙ</b> - военный конвой
👑 <b>НАКАЗАНИЯ ЛИДЕРАМ</b> - наказания лидерам
📊 <b>ПРОГРЕССИЯ</b> - уровни ОПГ
ℹ️ <b>ПОМОЩЬ</b> - помощь по боту
    """
    bot.send_message(message.chat.id, welcome_text, parse_mode='HTML', reply_markup=get_sections_keyboard())

@bot.message_handler(func=lambda message: message.text == "ℹ️ ПОМОЩЬ")
def help_section(message):
    user_id = message.from_user.id
    if user_id not in user_agreement or user_agreement[user_id] < 3:
        bot.send_message(message.chat.id, "⚠️ <b>Вы не ознакомились с правилами. Нажмите /start</b>", parse_mode='HTML')
        return
    
    help_text = """
📚 <b>ПОМОЩЬ ПО БОТУ:</b>

✅ <b>Как пользоваться:</b>
1. Выберите нужный раздел
2. Нажмите на интересующий вопрос
3. Получите точный ответ

📝 <b>Можно также писать свои вопросы:</b>
• "что такое дм"
• "со скольки нападать на вч"
• "1 уровень прогрессии"
• "варны в инкассации"

📊 <b>Статистика:</b> /stats

❓ Если бот не отвечает - @homa_suicide
    """
    bot.send_message(message.chat.id, help_text, parse_mode='HTML', reply_markup=get_sections_keyboard())

@bot.message_handler(func=lambda message: message.text == "📚 РП ТЕРМИНЫ")
def rp_terms_section(message):
    user_id = message.from_user.id
    if user_id not in user_agreement or user_agreement[user_id] < 3:
        bot.send_message(message.chat.id, "⚠️ <b>Вы не ознакомились с правилами. Нажмите /start</b>", parse_mode='HTML')
        return
    bot.send_message(message.chat.id, "📚 <b>Выберите термин:</b>", parse_mode='HTML', reply_markup=get_rp_terms_keyboard())

@bot.message_handler(func=lambda message: message.text == "⚔️ КАПТ")
def capt_section(message):
    user_id = message.from_user.id
    if user_id not in user_agreement or user_agreement[user_id] < 3:
        bot.send_message(message.chat.id, "⚠️ <b>Вы не ознакомились с правилами. Нажмите /start</b>", parse_mode='HTML')
        return
    bot.send_message(message.chat.id, "⚔️ <b>Выберите вопрос про капт:</b>", parse_mode='HTML', reply_markup=get_capt_keyboard())

@bot.message_handler(func=lambda message: message.text == "🏰 ВЧ")
def vch_section(message):
    user_id = message.from_user.id
    if user_id not in user_agreement or user_agreement[user_id] < 3:
        bot.send_message(message.chat.id, "⚠️ <b>Вы не ознакомились с правилами. Нажмите /start</b>", parse_mode='HTML')
        return
    bot.send_message(message.chat.id, "🏰 <b>Выберите вопрос про ВЧ:</b>", parse_mode='HTML', reply_markup=get_vch_keyboard())

@bot.message_handler(func=lambda message: message.text == "💰 ИНКАССАЦИЯ")
def incass_section(message):
    user_id = message.from_user.id
    if user_id not in user_agreement or user_agreement[user_id] < 3:
        bot.send_message(message.chat.id, "⚠️ <b>Вы не ознакомились с правилами. Нажмите /start</b>", parse_mode='HTML')
        return
    bot.send_message(message.chat.id, "💰 <b>Выберите вопрос про инкассацию:</b>", parse_mode='HTML', reply_markup=get_incass_keyboard())

@bot.message_handler(func=lambda message: message.text == "👤 ПОХИЩЕНИЕ")
def kidnap_section(message):
    user_id = message.from_user.id
    if user_id not in user_agreement or user_agreement[user_id] < 3:
        bot.send_message(message.chat.id, "⚠️ <b>Вы не ознакомились с правилами. Нажмите /start</b>", parse_mode='HTML')
        return
    bot.send_message(message.chat.id, "👤 <b>Выберите вопрос про похищение:</b>", parse_mode='HTML', reply_markup=get_kidnap_keyboard())

@bot.message_handler(func=lambda message: message.text == "🚚 КОНВОЙ")
def convoy_section(message):
    user_id = message.from_user.id
    if user_id not in user_agreement or user_agreement[user_id] < 3:
        bot.send_message(message.chat.id, "⚠️ <b>Вы не ознакомились с правилами. Нажмите /start</b>", parse_mode='HTML')
        return
    bot.send_message(message.chat.id, "🚚 <b>Выберите вопрос про конвой:</b>", parse_mode='HTML', reply_markup=get_convoy_keyboard())

@bot.message_handler(func=lambda message: message.text == "👑 НАКАЗАНИЯ ЛИДЕРАМ")
def leader_section(message):
    user_id = message.from_user.id
    if user_id not in user_agreement or user_agreement[user_id] < 3:
        bot.send_message(message.chat.id, "⚠️ <b>Вы не ознакомились с правилами. Нажмите /start</b>", parse_mode='HTML')
        return
    bot.send_message(message.chat.id, "👑 <b>Выберите вопрос про наказания лидерам:</b>", parse_mode='HTML', reply_markup=get_leader_keyboard())

@bot.message_handler(func=lambda message: message.text == "📊 ПРОГРЕССИЯ")
def progress_section(message):
    user_id = message.from_user.id
    if user_id not in user_agreement or user_agreement[user_id] < 3:
        bot.send_message(message.chat.id, "⚠️ <b>Вы не ознакомились с правилами. Нажмите /start</b>", parse_mode='HTML')
        return
    bot.send_message(message.chat.id, "📊 <b>Выберите уровень прогрессии:</b>", parse_mode='HTML', reply_markup=get_progress_keyboard())

@bot.message_handler(commands=['stats'])
def send_stats(message):
    update_stats(message.from_user.id)
    user_id = message.from_user.id
    if user_id not in user_agreement or user_agreement[user_id] < 3:
        bot.send_message(message.chat.id, "⚠️ <b>Вы не ознакомились с правилами. Нажмите /start</b>", parse_mode='HTML')
        return
    
    today = datetime.now().strftime("%Y-%m-%d")
    week_ago = datetime.now() - timedelta(days=7)
    total_day = stats["daily"].get(today, 0)
    total_week = sum(count for date, count in stats["daily"].items() if datetime.strptime(date, "%Y-%m-%d") >= week_ago)
    unique_users = len(user_ids)
    
    text = f"📊 <b>СТАТИСТИКА:</b>\n👤 Пользователей: {unique_users}\n📅 Сегодня: {total_day}\n📆 Неделя: {total_week}\n📚 Файлов: {len(RULES)}"
    bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=get_sections_keyboard())

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    update_stats(message.from_user.id)
    user_id = message.from_user.id
    
    if user_id not in user_agreement or user_agreement[user_id] < 3:
        bot.send_message(message.chat.id, "⚠️ <b>Вы не ознакомились с правилами. Нажмите /start</b>", parse_mode='HTML')
        return
    
    query = message.text.strip()
    
    # Пропускаем кнопки разделов
    if query in ["📚 РП ТЕРМИНЫ", "⚔️ КАПТ", "🏰 ВЧ", "💰 ИНКАССАЦИЯ", "👤 ПОХИЩЕНИЕ", 
                 "🚚 КОНВОЙ", "👑 НАКАЗАНИЯ ЛИДЕРАМ", "📊 ПРОГРЕССИЯ", "ℹ️ ПОМОЩЬ", "🔙 НАЗАД"]:
        return
    
    # Пропускаем кнопки терминов
    if query in ["ДМ", "ДБ", "СК", "ТК", "РП", "МГ", "ГМ", "ПГ", "РК", "БХ", "УК", "АК", "ЗЗ", "ФР", "ФМ", "ФФ", "ЦК", "УРП", "ТДМ", "МДМ", "ОРП", "ЕПП", "ПК", "ФЦК", "OOC", "IC", "все термины"]:
        return
    
    bot.send_chat_action(message.chat.id, 'typing')
    answer = find_answer(query)
    
    if answer:
        bot.send_message(message.chat.id, answer, parse_mode='HTML')
    else:
        bot.send_message(message.chat.id, f"❌ Не найден ответ на: {query}\n\nПопробуйте выбрать раздел из меню.", parse_mode='HTML')

# ======================== ЗАПУСК ========================
if __name__ == '__main__':
    print("="*60)
    print("🤖 Бот для обзвонов на Ghetto")
    print("="*60)
    print(f"📁 Папка: {os.getcwd()}")
    print(f"📚 Загружено файлов: {len(RULES)}")
    print("="*60)
    print("🚀 Бот запущен и готов к работе!")
    print("🔄 Нажми Ctrl+C для остановки")
    print("="*60)
    
    def signal_handler(sig, frame):
        print("\n👋 Бот остановлен")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        time.sleep(5)