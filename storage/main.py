from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

import pandas as pd
from io import BytesIO

import psycopg2
from psycopg2 import sql

import openpyxl
import os

# TODO: сделать чтобы писало какой не хватает колонки
# TODO: сделать считывание cred'ov из env

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_USER = 'ivanovo'
DB_PASSWORD = 'ivanovo'
DB_HOST = 'localhost'
DB_NAME = 'ivanovo'


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


@app.post("/upload_file/11")
async def upload_file_11(file: UploadFile = File(...)):
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


@app.post("/upload_file/5/{sheet_name}")
async def upload_file_5(sheet_name: str, file: UploadFile = File(...)):
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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
