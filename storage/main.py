from typing import List

from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import requests

import pandas as pd
from io import BytesIO

import psycopg2
from psycopg2 import sql

import openpyxl
import os
import ast

from jwt import ExpiredSignatureError, exceptions as jwt_exceptions


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_PORT = os.getenv('DB_PORT')
DB_HOST = os.getenv('DB_HOST')
API_KEY = os.getenv('API_KEY')
# API_KEY = 'd347483b-506b-451a-8071-87074574be00'


def tr(a):
    b = a.lstrip('{coordinates=').rstrip(', type=Polygon}').rstrip(', type=MultiPolygon}').replace("[", "{").replace("]", "}")

    try:
        return ast.literal_eval(b)
    except Exception as e:
        pass


def process_tables(table_8_path: str, table_9_path: str, table_13_path: str, table_14_path: str, table_11_path: str,
                   table_12_path: str):
    # Подключение 8 таблицы лист 1
    data_8 = pd.read_excel(table_8_path)

    # Переименовывание поля UNOM для объединения с таблицей 9
    data_8.rename(columns={'UNOM': 'unom'}, inplace=True)

    # Оставляем только уникальные уномы
    data_8.drop_duplicates(subset="unom", inplace=True)

    # Подключение 9 таблицы
    data_9 = pd.read_excel(table_9_path, header=1)

    # Переименовывание поля UNOM для объединения с таблицей 8
    data_9.rename(columns={'Unnamed: 11': 'unom'}, inplace=True)

    # Оставляем только уникальные уномы
    data_9.drop_duplicates(subset="unom", inplace=True)

    # Объединение 8 и 9 таблиц
    main_data = pd.merge(data_8, data_9, on='unom', how="outer")

    # Переименовывание некоторых полей
    main_data.rename(columns={'Unnamed: 12': 'UNAD'}, inplace=True)
    main_data.rename(columns={'Unnamed: 0': '№ п/п'}, inplace=True)

    # Подключение 13 таблицы
    data_13 = pd.read_excel(table_13_path)

    # Переименовывание поля UNOM для объединения 13 таблицы с предыдущими
    data_13.rename(columns={'UNOM': 'unom'}, inplace=True)

    # Приведение типов полей к string для объединения таблиц
    data_13['unom'] = data_13["unom"].astype('str')
    main_data['unom'] = main_data['unom'].astype('str')

    # Объединение с таблицей 13
    main_data_2 = pd.merge(main_data, data_13, on='unom', how="inner")

    """Преобразование таблицы 14"""

    # Нормализация значений из таблицы 14
    data = pd.read_excel(table_14_path, header=1)
    col_758_dict = pd.read_excel(table_14_path, sheet_name='COL_758')
    col_758_dict = dict(zip(col_758_dict['Объекты модели - Серии проектов (323)'], col_758_dict['Unnamed: 1']))
    col_781_dict = pd.read_excel(table_14_path, sheet_name='COL_781')
    col_781_dict = dict(zip(col_781_dict['Объекты модели - Материалы кровли по БТИ (988)'], col_781_dict['Unnamed: 1']))
    col_769_dict = pd.read_excel(table_14_path, sheet_name='COL_769')
    col_769_dict = dict(
        zip([str(i) for i in col_769_dict['Объекты модели - Материалы стен (305)']], col_769_dict['Unnamed: 1']))
    col_775_dict = pd.read_excel(table_14_path, sheet_name='COL_775')
    col_775_dict = dict(zip([str(i) for i in col_775_dict['Объекты модели - Очередность уборки кровли (983)']],
                            col_775_dict['Unnamed: 1']))

    # заменяем айди на человекочитаемые значения
    data['Серии проектов'] = data['Серии проектов'].apply(lambda x: col_758_dict[x])
    data['Материалы кровли по БТИ'] = data['Материалы кровли по БТИ'].apply(
        lambda x: col_781_dict[x] if x in col_781_dict.keys() else -1)
    data[' Материалы стен'] = data[' Материалы стен'].apply(
        lambda x: col_769_dict[str(x)] if str(x) in col_769_dict.keys() else -1)

    # Объединение таблицы 11 и приведение к нормализованным значениям
    data_11 = pd.read_excel(table_11_path)
    data_11 = data_11.groupby('UNOM', as_index=False).agg({
        'Потребители': lambda x: list(x.unique())[0],
        'Группа': lambda x: list(x.unique())[0],
        'Центральное отопление(контур)': lambda x: list(x.unique())[0],
        'Марка счетчика ': lambda x: list(x.unique())[0],
        'Серия/Номер счетчика': lambda x: list(x.unique())[0],

    })

    # Переименовывание поля UNOM для объединения 1 таблицы с предыдущими
    data.rename(columns={'УНОМ': 'unom'}, inplace=True)
    data_11.rename(columns={'UNOM': 'unom'}, inplace=True)

    # Переименовывание поля UNOM к типу string
    data['unom'] = data["unom"].astype('str')
    data_11['unom'] = data_11['unom'].astype('str')

    # Объединение таблиц 11 и 14
    data_11_14 = pd.merge(data, data_11, on="unom", how="outer")

    # Переименовывание поля UNOM к типу string
    data_11_14["unom"] = data_11_14["unom"].astype("str")
    main_data_2["unom"] = main_data_2["unom"].astype("str")

    # Объединение таблиц 11 и 14 с предыдущими
    merged_data = pd.merge(data_11_14, main_data_2, on="unom", how="inner")

    merged_data.rename(columns={'P2': 'Внутригородская территория'}, inplace=True)

    # Подключение 8 таблицы 2 лист
    numbers = pd.read_excel(table_8_path, sheet_name=1)

    # Переименовывание поля номера ОДС для последующего объединения
    numbers.rename(columns={"NAME": "№ ОДС"}, inplace=True)

    # Объединение таблицы с номерами ОДС
    agg_data = pd.merge(merged_data, numbers, on="№ ОДС", how="outer")

    # Подключение 12 таблицы
    data12 = pd.read_excel(table_12_path)

    db = agg_data

    # Нормализация адресов для дальнейшего объединения с таблицей 12
    import re

    # Пример данных
    data = {
        'first': data12["Департамент"],
        'second': db["Полный адрес"]
    }
    df = pd.DataFrame(data)

    # Замена пустых значений на пустые строки
    df['first'] = df['first'].fillna('')
    df['second'] = df['second'].fillna('')

    # Функция для нормализации адресов
    def normalize_address(address):
        address = address.strip().lower()  # Удаление пробелов и приведение к нижнему регистру
        address = re.sub(r'\s+', ' ', address)  # Замена множественных пробелов одним пробелом
        address = re.sub(r'\bул\b', 'улица', address)  # Замена сокращений
        address = re.sub(r'\bд\b', 'дом', address)
        address = re.sub(r'\bпр\b', 'проезд', address)
        address = re.sub(r'\bпр-т\b', 'проспект', address)
        address = re.sub(r'\bпросп\b', 'проспект', address)
        address = re.sub(r'\bпер\b', 'переулок', address)
        address = re.sub(r'\bк\b', 'корпус', address)
        address = re.sub(r'\bкорп\b', 'корпус', address)
        address = re.sub(r'\bстр\b', 'строение', address)
        address = re.sub(r'[,.]', ' ', address)  # Удаление точек и запятых

        # Приведение адреса к нужному формату
        address = re.sub(r'\bгород\b', '', address)  # Удаление слова "город"
        address = re.sub(r'\bмосква\b', '', address)  # Добавление "город Москва"
        address = re.sub(r'\bулица\b', 'улица', address)
        address = re.sub(r'\bдом\b', 'дом', address)
        address = re.sub(r'\bкорпус\b', 'корпус', address)
        address = re.sub(r'\bстроение\b', 'строение', address)

        # Удаление лишних пробелов
        address = re.sub(r'\s+', ' ', address).strip()

        return address

    # Применение нормализации к столбцам 'first' и 'second'
    df['normalized_first'] = df['first'].apply(normalize_address)
    df['normalized_second'] = df['second'].apply(normalize_address)

    # Объединение с 12 таблицей с помощью нормализации адресов
    new_db = db
    new_db["Полный адрес"] = new_db['Полный адрес'].astype('str')
    data12["Департамент"] = data12['Департамент'].astype('str')
    new_db["Полный адрес"] = new_db['Полный адрес'].apply(normalize_address)
    data12["Департамент"] = data12["Департамент"].apply(normalize_address)
    data12.rename(columns={"Департамент": "Полный адрес"}, inplace=True)
    merged_db = pd.merge(new_db, data12, on="Полный адрес", how="left")
    merged_db["Класс энергоэффективности здания"] = merged_db["Класс энергоэффективности здания"].combine_first(
        pd.Series(['C'] * len(merged_db)))

    # Приведение поля "Полный адрес" к исходному виду от нормализованного
    merged_db["Полный адрес"] = db["Полный адрес"]

    import random
    def generate_moscow_phone_number(h):
        three_digit_number = str(random.randint(500, 999))
        phone_number = f"+7 ({three_digit_number}) {random.randint(0, 999):03d}-{random.randint(0, 99):02d}-{random.randint(0, 99):02d}"
        return phone_number

    phones = {
        'Полный адрес': ["город Москва, посёлок Акулово, дом 27", "город Москва, улица Чечулина, дом 3, корпус 2",
                         "город Москва, Сахалинская улица, дом 4А", "город Москва, Новокосинская улица, дом 9А",
                         "город Москва, Суздальская улица, дом 10А", "город Москва, 3-я Владимирская улица, дом 3А",
                         "город Москва, улица Стромынка, дом 10, строение 1"],
        'Телефон': ["+7 (495) 469-59-86", "+7 (499) 181-24-62", "+7 (495) 466-92-88", "+7 (495) 700-05-74",
                    "+7 (495) 702-01-69", "+7 (495) 304-97-05", "+7 (499) 785-25-14"]
    }
    phones_df = pd.DataFrame(phones)

    merged_db_1 = pd.merge(merged_db, phones_df, on="Полный адрес", how="left")

    empty_phone_rows = merged_db_1['Телефон'].isna()
    merged_db_1.loc[empty_phone_rows, 'Телефон'] = merged_db_1.loc[empty_phone_rows, 'Телефон'].apply(
        generate_moscow_phone_number)

    def select_working_hours():
        options = ["Круглосуточно", "9:00 - 21:00", "9:00 – 18:00"]
        return random.choice(options)

    merged_db_1['Режим работы'] = merged_db_1.apply(lambda _: select_working_hours(), axis=1)

    merged_db_1.drop(
        ["Всего строений", "Общая площадь, м²", "Отапливаемая площадь, м²", "Среднее количество работников, чел.",
         "Тип учреждения / Тип строения", "Год ввода здания в эксплуатацию",
         "Количество входов", "Фактический износ здания, %", "Количество лифтов", "Этажность_y", "L5_VALUE", "L5_TYPE",
         "L4_VALUE", "L4_TYPE", "L3_VALUE", "L3_TYPE", "L2_VALUE", "P0", "L2_TYPE", "L1_VALUE",
         "P91", "SIMPLE_ADDRESS", "P90", "P6", "P4", "P3", "P1", "OnTerritoryOfMoscow", "Общая площадь_y",
         "Этажность_x", "Потребитель (или УК)", "Группа_y", "Округ_y", "Адрес", "Unnamed: 19", "ADDRESS_y"], axis=1,
        inplace=True)

    # Замена названий финальной таблицы
    merged_db_1.rename(columns={"L1_TYPE": "Тип номера дома, владения, участка",
                                "P7": "Наименование элемента планировочной структуры или улично-дорожной сети",
                                "P5": "Муниципальный округ.1", "Общая площадь_x": "Общая площадь", "Округ_x": "Округ",
                                " Материалы стен": "Материалы стен", "Группа_x": "Группа"}, inplace=True)

    merged_db_1.to_csv("output_aggr.csv", index=False)

    return "output_aggr.csv"


def get_db():
    try:
        conn = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,  # локальный хост
            port="5432",  # стандартный порт PostgreSQL
            database=DB_NAME
        )
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail="error while connecting to db" + str(e))


def authorize(token: str) -> bool:
    try:
        if token == 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MjIxNDM4NzcsIklEIjoxLCJVc2VyVHlwZSI6IiJ9.4Dvv-2I4sFpwsBMEJA3HTjyh8PrbEtfgXikDx54xXog':
            return True
        elif token == '':
            raise ExpiredSignatureError
        else:
            raise jwt_exceptions.DecodeError
    except ExpiredSignatureError:
        raise HTTPException(401, detail='jwt expired')
    except jwt_exceptions.DecodeError:
        raise HTTPException(401, detail='wrong jwt')


def load_csv_to_db(file_path: str, table_name: str):
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        copy_sql = sql.SQL("""
                COPY {} FROM STDIN WITH CSV HEADER DELIMITER ','
            """).format(sql.Identifier(table_name))

        with open(file_path, 'r') as f:
            cursor.copy_expert(copy_sql, f)

        conn.commit()
        cursor.close()
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail="Error while importing CSV to DB: " + str(e))
    finally:
        if conn:
            conn.close()


def get_center(address):
    res = requests.get(f'https://geocode-maps.yandex.ru/1.x/?apikey={API_KEY}&geocode={address}&format=json')
    if res.status_code == 200:
        try:
            pos = res.json()["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"]
            center = list(map(lambda x: round(float(x), 8), pos.split()))
            return center
        except (IndexError, KeyError):
            return [0, 0]
    else:
        print(res.status_code, res.text)
        return [0, 0]


@app.post("/upload_file/11/{token}")
async def upload_file_11(token: str, file: UploadFile = File(...)):
    authorize(token)

    if file.content_type != 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        return {"error": "Invalid file type. Please upload an XLSX file."}

    contents = await file.read()
    df = pd.read_excel(BytesIO(contents))

    file_name = 'output_11.csv'

    # df.to_csv(file_name, index=False, sep=',', encoding='utf-8')

    df = df.rename(columns={
        'ID УУ': 'id_uu',  # 'ID УУ': 'id_uu',
        'ID ТУ': 'id_tu',
        'Округ': 'district',
        'Район': 'area',
        'Потребители': 'consumers',
        'Группа': 'group_type',
        'UNOM': 'unom',
        'Адрес': 'address',
        'Центральное отопление(контур)': 'central_heating_contour',
        'Марка счетчика ': 'meter_brand',
        'Серия/Номер счетчика': 'meter_serial_number',
        'Дата': 'date',
        'Месяц/Год': 'month_year',
        'Unit': 'unit',
        'Объём поданого теплоносителя в систему ЦО': 'volume_supplied',
        'Объём обратного теплоносителя из системы ЦО': 'volume_returned',
        'Разница между подачей и обраткой(Подмес)': 'difference_supply_return_mix',
        'Разница между подачей и обраткой(Утечка)': 'difference_supply_return_leak',
        'Температура подачи': 'temperature_supply',
        'Температура обратки': 'temperature_return',
        'Наработка часов счётчика': 'meter_operating_hours',
        'Расход тепловой энергии ': 'heat_energy_consumption',
        'Ошибки': 'errors'
    })

    correct_order = [
        'unom', 'id_uu', 'id_tu', 'district', 'area', 'consumers', 'group_type', 'address',
        'central_heating_contour', 'meter_brand', 'meter_serial_number', 'month_year',
        'unit', 'volume_supplied', 'volume_returned', 'difference_supply_return_mix',
        'difference_supply_return_leak', 'temperature_supply', 'temperature_return',
        'meter_operating_hours', 'heat_energy_consumption', 'errors'
    ]

    df = df.drop(columns=['date'])

    missing_columns = set(correct_order) - set(df.columns)
    if missing_columns:
        raise HTTPException(status_code=400, detail=f"Отсутствуют столбцы: {missing_columns}")

    df = df[correct_order]

    df.to_csv(file_name, index=False, sep=',', encoding='utf-8')

    load_csv_to_db(file_name, 'heating_data')

    try:
        os.remove(file_name)
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {e}")

    return {"filename": file.filename}


@app.post("/upload_file/5/{sheet_name}/{token}")
async def upload_file_5(sheet_name: str, token: str, file: UploadFile = File(...)):
    authorize(token)

    if file.content_type != 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        return {"error": "Invalid file type. Please upload an XLSX file."}

    contents = await file.read()
    df = pd.read_excel(BytesIO(contents), sheet_name=sheet_name)

    file_name = 'output_5.csv'

    # df.to_csv(file_name, index=False, sep=',', encoding='utf-8')

    df = df.rename(columns={
        'Наименование': 'name',
        'Источник': 'source',
        'Дата создания во внешней системе': 'creation_date',
        'Дата закрытия': 'closure_date',
        'Округ': 'district',
        'УНОМ': 'unom',
        'Адрес': 'address',
        'Дата и время завершения события во внешней системе': 'event_completion_date'
    })

    correct_order = [
        'name', 'source', 'creation_date', 'closure_date', 'district', 'unom', 'address', 'event_completion_date'
    ]

    missing_columns = set(correct_order) - set(df.columns)
    if missing_columns:
        df = df.rename(columns={
            'Дата и время завершения события': 'event_completion_date'
        })
        missing_columns = set(correct_order) - set(df.columns)
        if missing_columns:
            raise HTTPException(status_code=400, detail=f"Отсутствуют столбцы: {missing_columns}")

    df = df[correct_order]

    filter_values = [
        'P1 <= 0', 'P2 <= 0', 'T1 < min', 'T1 > max', 'Аварийная протечка труб в подъезде',
        'Крупные пожары', 'Отсутствие отопления в доме', 'Протечка труб в подъезде',
        'Сильная течь в системе отопления', 'Температура в квартире ниже нормативной',
        'Температура в помещении общего пользования ниже нормативной', 'Течь в системе отопления'
    ]

    df = df[df['name'].isin(filter_values)]

    df['unom'] = df['unom'].apply(lambda x: int(str(x).replace('.0', '')))

    df.to_csv(file_name, index=False, sep=',', encoding='utf-8')

    load_csv_to_db(file_name, 'events')

    try:
        os.remove(file_name)
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {e}")

    return {"filename": file.filename}


@app.post("/upload_file/7/{token}")
async def upload_file_7(token: str, file: UploadFile = File(...)):
    authorize(token)

    if file.content_type != 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        return {"error": "Invalid file type. Please upload an XLSX file."}

    contents = await file.read()
    df = pd.read_excel(BytesIO(contents))

    df = df.iloc[:, :-5]

    df = df.drop_duplicates()

    file_name = 'output_7.csv'

    df = df.rename(columns={
        '№ п/п': 'id',
        'Номер ТП': 'ctp_id',
        'Адрес ТП': 'address',
        'Вид ТП': 'type',
        'Тип по размещению': 'placement_type',
        'Источник теплоснабжения': 'source',
        'Административный округ (ТП)': 'administrative',
        'Муниципальный район': 'municipal',
        'Дата ввода в эксплуатацию': 'start_date',
        'Балансодержатель': 'balance_holder',
        'Адрес строения': 'building_address',
    })

    df = df.drop(columns=['building_address'])

    correct_order = [
        'id',
        'ctp_id',
        'address',
        'type',
        'placement_type',
        'source',
        'administrative',
        'municipal',
        'start_date',
        'balance_holder',
        'center'
    ]

    df['center'] = df['address'].apply(get_center)
    df['center'] = df['center'].apply(lambda x: '{' + ','.join(map(str, x)) + '}')

    df = df[correct_order]

    missing_columns = set(correct_order) - set(df.columns)
    if missing_columns:
        raise HTTPException(status_code=400, detail=f"Отсутствуют столбцы: {missing_columns}")

    df.to_csv(file_name, index=False, sep=',', encoding='utf-8')

    load_csv_to_db(file_name, 'ctps')

    try:
        os.remove(file_name)
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {e}")

    return {"filename": file.filename}


@app.post("/upload_file/aggregated/{token}")
async def upload_file_aggregated(
        token: str,
        table_8: UploadFile = File(...),
        table_9: UploadFile = File(...),
        table_13: UploadFile = File(...),
        table_14: UploadFile = File(...),
        table_11: UploadFile = File(...),
        table_12: UploadFile = File(...)
):
    authorize(token)

    files = {"table_8": table_8, "table_9": table_9, "table_13": table_13,
             "table_14": table_14, "table_11": table_11, "table_12": table_12}
    for file_name in files.keys():
        file = files[file_name]
        if file.content_type != 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
            return {"error": "Invalid file type. Please upload an XLSX file."}

    for file_name in files.keys():
        contents = await files[file_name].read()

        file_path = f"{file_name}.xlsx"
        with open(file_path, "wb") as f:
            f.write(contents)

    file_path = process_tables("table_8.xlsx", "table_9.xlsx", "table_13.xlsx",
                               "table_14.xlsx", "table_11.xlsx", "table_12.xlsx")

    df = pd.read_csv(file_path)

    file_name = 'aggregared_processed.csv'

    df = df.rename(columns={
        'Адрес из сторонней системы': 'external_system_address',
        'Адрес по БТИ': 'bti_address',
        'Округ': 'district',
        'Район': 'area',
        'Серии проектов': 'project_series',
        'Количество этажей': 'number_of_floors',
        'Количество подъездов': 'number_of_entrances',
        'Количество квартир': 'number_of_apartments',
        'Общая площадь': 'total_area',
        'Общая площадь жилых помещений': 'total_residential_area',
        'Общая площадь нежилых помещений': 'total_non_residential_area',
        'Износ объекта (по БТИ)': 'wear_and_tear_bti',
        'Материалы стен': 'wall_materials',
        'Признак аварийности здания': 'emergency_status',
        'Количество пассажирских лифтов': 'number_of_passenger_elevators',
        'Количество грузопассажирских лифтов': 'number_of_freight_elevators',
        'Очередность уборки кровли': 'roof_cleaning_priority',
        'Материалы кровли по БТИ': 'roof_materials',
        'Типы жилищного фонда': 'housing_fund_types',
        'Статусы МКД': 'mkd_statuses',
        'Потребители': 'consumers',
        'Группа': 'group_type',
        'Центральное отопление(контур)': 'central_heating',
        'Марка счетчика ': 'meter_brand',
        'Серия/Номер счетчика': 'meter_serial_number',
        'ID УУ': 'id_uu',
        'Полный адрес': 'full_address',
        '№ ОДС': 'ods_number',
        'Адрес ОДС': 'ods_address',
        'ЦТП': 'ctp',
        '№ п/п': 'serial_number',
        'Город': 'city',
        'Административный округ': 'administrative_district',
        'Муниципальный округ': 'municipal_district',
        'Населенный пункт': 'locality',
        'Улица': 'street',
        'Тип номера дом': 'house_number_type',
        'Номер дома': 'house_number',
        'Номер корпуса': 'building_number',
        'Тип номера строения/сооружения': 'structure_number_type',
        'Номер строения': 'structure_number',
        'UNAD': 'unad',
        'Материал': 'material',
        'Назначение': 'purpose',
        'Класс': 'class',
        'Тип': 'type',
        'Признак': 'sign',
        'global_id': 'global_id',
        'OBJ_TYPE': 'obj_type',
        'ADDRESS_x': 'address_x',
        'Муниципальный округ.1': 'municipal_district_1',
        'Наименование элемента планировочной структуры или улично-дорожной сети': 'planning_element_name',
        'Тип номера дома, владения, участка': 'house_ownership_number_type',
        'Внутригородская территория': 'intra_city_area',
        'ADM_AREA': 'adm_area',
        'DISTRICT': 'district_1',
        'NREG': 'nreg',
        'DREG': 'dreg',
        'N_FIAS': 'n_fias',
        'D_FIAS': 'd_fias',
        'KAD_N': 'kad_n',
        'KAD_ZU': 'kad_zu',
        'KLADR': 'kladr',
        'TDOC': 'tdoc',
        'NDOC': 'ndoc',
        'DDOC': 'ddoc',
        'ADR_TYPE': 'adr_type',
        'VID': 'vid',
        'SOSTAD': 'sostad',
        'STATUS': 'status',
        'geoData': 'geo_data',
        'geodata_center': 'geo_data_center',
        'ID ODS': 'id_ods',
        'PHONE_NUMBER': 'phone_number',
        'Класс энергоэффективности здания': 'energy_efficiency_class',
        'Телефон': 'phone_number_new',
        'Режим работы': 'work_hours'
    })

    correct_order = [
        'unom',
        'ctp',
        'external_system_address',
        'bti_address',
        'district',
        'area',
        'project_series',
        'number_of_floors',
        'number_of_entrances',
        'number_of_apartments',
        'total_area',
        'total_residential_area',
        'total_non_residential_area',
        'wear_and_tear_bti',
        'wall_materials',
        'emergency_status',
        'number_of_passenger_elevators',
        'number_of_freight_elevators',
        'roof_cleaning_priority',
        'roof_materials',
        'housing_fund_types',
        'mkd_statuses',
        'consumers',
        'group_type',
        'central_heating',
        'meter_brand',
        'meter_serial_number',
        'id_uu',
        'full_address',
        'ods_number',
        'ods_address',
        'serial_number',
        'city',
        'administrative_district',
        'municipal_district',
        'locality',
        'street',
        'house_number_type',
        'house_number',
        'building_number',
        'structure_number_type',
        'structure_number',
        'unad',
        'material',
        'purpose',
        'class',
        'type',
        'sign',
        'global_id',
        'obj_type',
        'address_x',
        'planning_element_name',
        'house_ownership_number_type',
        'intra_city_area',
        'adm_area',
        'district_1',
        'nreg',
        'dreg',
        'n_fias',
        'd_fias',
        'kad_n',
        'kad_zu',
        'kladr',
        'tdoc',
        'ndoc',
        'ddoc',
        'adr_type',
        'vid',
        'sostad',
        'status',
        'geo_data',
        'geo_data_center',
        'id_ods',
        'phone_number',
        'energy_efficiency_class',
        'phone_number_new',
        'work_hours'
    ]

    df = df[correct_order]

    df = df.dropna(subset=['unom'])
    df['unom'] = df['unom'].apply(lambda x: int(str(x).replace('.0', '')))
    df['geo_data'] = df['geo_data'].apply(lambda x: tr(x) if x else None)
    df['geo_data_center'] = df['geo_data_center'].apply(lambda x: tr(x) if x else None)

    df = df.drop_duplicates(subset=['unom'], keep='first')

    missing_columns = set(correct_order) - set(df.columns)
    if missing_columns:
        raise HTTPException(status_code=400, detail=f"Отсутствуют столбцы: {missing_columns}")

    df.to_csv(file_name, index=False, sep=',', encoding='utf-8')

    load_csv_to_db(file_name, 'buildings')

    try:
        os.remove(file_path)
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {e}")
    try:
        os.remove(file_name)
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {e}")

    return {"filename": file_name}


@app.post("/upload_file/aggregated")
async def upload_file_aggregated(
        token: str,
        table_8: UploadFile = File(...),
        table_9: UploadFile = File(...),
        table_13: UploadFile = File(...),
        table_14: UploadFile = File(...),
        table_11: UploadFile = File(...),
        table_12: UploadFile = File(...)
):
    authorize(token)

    files = {"table_8": table_8, "table_9": table_9, "table_13": table_13,
             "table_14": table_14, "table_11": table_11, "table_12": table_12}
    for file_name in files.keys():
        file = files[file_name]
        if file.content_type != 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
            return {"error": "Invalid file type. Please upload an XLSX file."}

    for file_name in files.keys():
        contents = await files[file_name].read()

        file_path = f"{file_name}.xlsx"
        with open(file_path, "wb") as f:
            f.write(contents)

    file_path = process_tables("table_8.xlsx", "table_9.xlsx", "table_13.xlsx",
                               "table_14.xlsx", "table_11.xlsx", "table_12.xlsx")

    df = pd.read_csv(file_path)

    file_name = 'aggregared_processed.csv'

    df = df.rename(columns={
        'Адрес из сторонней системы': 'external_system_address',
        'Адрес по БТИ': 'bti_address',
        'Округ': 'district',
        'Район': 'area',
        'Серии проектов': 'project_series',
        'Количество этажей': 'number_of_floors',
        'Количество подъездов': 'number_of_entrances',
        'Количество квартир': 'number_of_apartments',
        'Общая площадь': 'total_area',
        'Общая площадь жилых помещений': 'total_residential_area',
        'Общая площадь нежилых помещений': 'total_non_residential_area',
        'Износ объекта (по БТИ)': 'wear_and_tear_bti',
        'Материалы стен': 'wall_materials',
        'Признак аварийности здания': 'emergency_status',
        'Количество пассажирских лифтов': 'number_of_passenger_elevators',
        'Количество грузопассажирских лифтов': 'number_of_freight_elevators',
        'Очередность уборки кровли': 'roof_cleaning_priority',
        'Материалы кровли по БТИ': 'roof_materials',
        'Типы жилищного фонда': 'housing_fund_types',
        'Статусы МКД': 'mkd_statuses',
        'Потребители': 'consumers',
        'Группа': 'group_type',
        'Центральное отопление(контур)': 'central_heating',
        'Марка счетчика ': 'meter_brand',
        'Серия/Номер счетчика': 'meter_serial_number',
        'ID УУ': 'id_uu',
        'Полный адрес': 'full_address',
        '№ ОДС': 'ods_number',
        'Адрес ОДС': 'ods_address',
        'ЦТП': 'ctp',
        '№ п/п': 'serial_number',
        'Город': 'city',
        'Административный округ': 'administrative_district',
        'Муниципальный округ': 'municipal_district',
        'Населенный пункт': 'locality',
        'Улица': 'street',
        'Тип номера дом': 'house_number_type',
        'Номер дома': 'house_number',
        'Номер корпуса': 'building_number',
        'Тип номера строения/сооружения': 'structure_number_type',
        'Номер строения': 'structure_number',
        'UNAD': 'unad',
        'Материал': 'material',
        'Назначение': 'purpose',
        'Класс': 'class',
        'Тип': 'type',
        'Признак': 'sign',
        'global_id': 'global_id',
        'OBJ_TYPE': 'obj_type',
        'ADDRESS_x': 'address_x',
        'Муниципальный округ.1': 'municipal_district_1',
        'Наименование элемента планировочной структуры или улично-дорожной сети': 'planning_element_name',
        'Тип номера дома, владения, участка': 'house_ownership_number_type',
        'Внутригородская территория': 'intra_city_area',
        'ADM_AREA': 'adm_area',
        'DISTRICT': 'district_1',
        'NREG': 'nreg',
        'DREG': 'dreg',
        'N_FIAS': 'n_fias',
        'D_FIAS': 'd_fias',
        'KAD_N': 'kad_n',
        'KAD_ZU': 'kad_zu',
        'KLADR': 'kladr',
        'TDOC': 'tdoc',
        'NDOC': 'ndoc',
        'DDOC': 'ddoc',
        'ADR_TYPE': 'adr_type',
        'VID': 'vid',
        'SOSTAD': 'sostad',
        'STATUS': 'status',
        'geoData': 'geo_data',
        'geodata_center': 'geo_data_center',
        'ID ODS': 'id_ods',
        'PHONE_NUMBER': 'phone_number',
        'Класс энергоэффективности здания': 'energy_efficiency_class',
        'Телефон': 'phone_number_new',
        'Режим работы': 'work_hours'
    })

    correct_order = [
        'unom',
        'ctp',
        'external_system_address',
        'bti_address',
        'district',
        'area',
        'project_series',
        'number_of_floors',
        'number_of_entrances',
        'number_of_apartments',
        'total_area',
        'total_residential_area',
        'total_non_residential_area',
        'wear_and_tear_bti',
        'wall_materials',
        'emergency_status',
        'number_of_passenger_elevators',
        'number_of_freight_elevators',
        'roof_cleaning_priority',
        'roof_materials',
        'housing_fund_types',
        'mkd_statuses',
        'consumers',
        'group_type',
        'central_heating',
        'meter_brand',
        'meter_serial_number',
        'id_uu',
        'full_address',
        'ods_number',
        'ods_address',
        'serial_number',
        'city',
        'administrative_district',
        'municipal_district',
        'locality',
        'street',
        'house_number_type',
        'house_number',
        'building_number',
        'structure_number_type',
        'structure_number',
        'unad',
        'material',
        'purpose',
        'class',
        'type',
        'sign',
        'global_id',
        'obj_type',
        'address_x',
        'planning_element_name',
        'house_ownership_number_type',
        'intra_city_area',
        'adm_area',
        'district_1',
        'nreg',
        'dreg',
        'n_fias',
        'd_fias',
        'kad_n',
        'kad_zu',
        'kladr',
        'tdoc',
        'ndoc',
        'ddoc',
        'adr_type',
        'vid',
        'sostad',
        'status',
        'geo_data',
        'geo_data_center',
        'id_ods',
        'phone_number',
        'energy_efficiency_class',
        'phone_number_new',
        'work_hours'
    ]

    df = df[correct_order]

    df = df.dropna(subset=['unom'])
    df['unom'] = df['unom'].apply(lambda x: int(str(x).replace('.0', '')))
    df['geo_data'] = df['geo_data'].apply(lambda x: tr(x) if x else None)
    df['geo_data_center'] = df['geo_data_center'].apply(lambda x: tr(x) if x else None)

    df = df.drop_duplicates(subset=['unom'], keep='first')

    missing_columns = set(correct_order) - set(df.columns)
    if missing_columns:
        raise HTTPException(status_code=400, detail=f"Отсутствуют столбцы: {missing_columns}")

    df.to_csv(file_name, index=False, sep=',', encoding='utf-8')

    load_csv_to_db(file_name, 'buildings')

    try:
        os.remove(file_path)
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {e}")
    try:
        os.remove(file_name)
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {e}")

    return {"filename": file_name}


@app.post("/upload_file/tecs/{token}")
async def upload_file_aggregated(token: str):
    authorize(token)
    file_path = "tecs_table.csv"
    load_csv_to_db(file_path, 'tecs')

    return {"status": "success!"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
