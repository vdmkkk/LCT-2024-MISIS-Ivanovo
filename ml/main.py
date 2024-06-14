import pandas as pd
import datetime
import json
import requests

from catboost import CatBoostClassifier
import numpy as np
import psycopg2

from fastapi import FastAPI, HTTPException
import uvicorn
import warnings

from typing import List

import os

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_PORT = os.getenv('DB_PORT')
DB_HOST = os.getenv('DB_HOST')

TIME_OUT = 20000000000  # milliseconds

warnings.filterwarnings("ignore")

app = FastAPI()

model = CatBoostClassifier()
model.load_model('model_task1')


@app.post("/predict_all/")
async def predict_all(date: datetime.datetime):
    try:
        conn = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,  # локальный хост
            port="5432",  # стандартный порт PostgreSQL
            database=DB_NAME
        )

        # Получаем предсказания
        preds = get_predict_for_all(model, date, conn)

        return preds

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        conn.close()


@app.post("/predict_one/")
async def predict_one(unom: int, date: datetime.datetime, n: int):
    try:
        conn = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,  # локальный хост
            port="5432",  # стандартный порт PostgreSQL
            database=DB_NAME
        )

        # Получаем предсказания
        preds = get_predict_for_one(model, unom, date, n, conn)

        return preds

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        conn.close()


features = [
    'УНОМ',
    'month',
    'mean_volume1forhour',
    'std_volume1forhour',
    'mean_volume2forhour',
    'std_volume2forhour',
    'mean_q2forhour',
    'std_q2forhour',
    'min_volume1forhour',
    'max_volume1forhour',
    'median_volume1forhour',
    'min_volume2forhour',
    'max_volume2forhour',
    'median_volume2forhour',
    'min_q2forhour',
    'max_q2forhour',
    'median_q2forhour',
    'Потребители',
    'Группа',
    'Центральное отопление(контур)',
    'Ошибки',
    'weather1',
    'weather2',
    'Округ',
    'Район',
    'Серии проектов',
    'Количество этажей',
    'Количество подъездов',
    'Количество квартир',
    'Общая площадь',
    'Общая площадь жилых помещений',
    'Износ объекта (по БТИ)',
    'Материалы стен',
    'Признак аварийности здания',
    'Количество пассажирских лифтов',
    'Количество грузопассажирских лифтов',
    'Материалы кровли по БТИ',
    'Типы жилищного фонда',
    'Статусы МКД',
    'Марка счетчика ',
    'ЦТП',
    'Муниципальный округ',
    'Материал',
    'Назначение',
    'Класс',
    'Тип',
    'OBJ_TYPE',
    'Внутригородская территория',
    'Давление не в норме_count',
    'T < min_count',
    'T > max_count',
    'Утечка_count',
    'month1_count',
    'month2_count',
    'month3_count',
    'month4_count',
    'month10_count',
    'month11_count',
    'month12_count',
    'year',
    'day',
    'hour',
    'dayofweek',
    'weekofyear',
    'quarter',
    'is_month_start',
    'is_month_end',
    'month_sin',
    'month_cos',
    'hour_sin',
    'hour_cos',
    'quarter_sin',
    'quarter_cos',
    'day_sin',
    'day_cos',
    'dayofweek_sin',
    'dayofweek_cos',
    'weekofyear_sin',
    'weekofyear_cos'
]

features2aggdata = [
    "УНОМ",
    'Округ',
    'Район',
    'Серии проектов',
    'Количество этажей',
    'Количество подъездов',
    'Количество квартир',
    'Общая площадь',
    'Общая площадь жилых помещений',
    'Износ объекта (по БТИ)',
    'Материалы стен',
    'Признак аварийности здания',
    'Количество пассажирских лифтов',
    'Количество грузопассажирских лифтов',
    'Материалы кровли по БТИ',
    'Типы жилищного фонда',
    'Статусы МКД',
    'Марка счетчика ',
    'ЦТП',
    'Муниципальный округ',
    'Материал',
    'Назначение',
    'Класс',
    'Тип',
    'OBJ_TYPE',
    'Внутригородская территория',

]

categorical_features = [
    'УНОМ',
    'month',
    'Потребители',
    'Группа',
    'Центральное отопление(контур)',
    'Ошибки',
    'Округ',
    'Район',
    'Серии проектов',
    'Материалы стен',
    'Признак аварийности здания',
    'Материалы кровли по БТИ',
    'Типы жилищного фонда',
    'Статусы МКД',
    'Марка счетчика ',
    'ЦТП',
    'Муниципальный округ',
    'Материал',
    'Назначение',
    'Класс',
    'Тип',
    'OBJ_TYPE',
    'Внутригородская территория',
    'is_month_start',
    'is_month_end'
]


def get_predict_for_all(model: CatBoostClassifier, date: datetime.datetime, conn) -> dict:
    agg_data = get_agg_data(conn)
    agg_data = agg_data.dropna(subset='unom')
    unomlst = agg_data['unom'].unique().tolist()
    n_preds = len(unomlst)
    events2preds = pd.DataFrame({
        "УНОМ": unomlst,
        "Дата создания во внешней системе": [date] * n_preds,
        "month": [date.month] * n_preds,
        "day": [date.day] * n_preds
    })

    odpu = get_odpu(date, conn)
    events2preds[ftrs2odpu] = events2preds.apply(lambda x: add_opdu_features(odpu, x), axis=1)

    with open('weather.json', 'r', encoding='utf-8') as file:
        weather = json.load(file)
    events2preds[['weather1', 'weather2']] = events2preds.apply(lambda x: collect_weather(x, weather), axis=1)

    events = get_events(date, conn)

    events2preds[feature2events] = events2preds.apply(lambda x: collect_events(x, events), axis=1)
    agg_data['УНОМ'] = agg_data['unom']
    events2preds = events2preds.merge(agg_data[features2aggdata], how='left', on='УНОМ')

    events2preds = extract_datetime_features(events2preds, "Дата создания во внешней системе")
    events2preds = add_cyclic_features(events2preds, 'month', 12)
    events2preds = add_cyclic_features(events2preds, 'hour', 24)
    events2preds = add_cyclic_features(events2preds, 'quarter', 4)
    events2preds = add_cyclic_features(events2preds, 'day', 31)
    events2preds = add_cyclic_features(events2preds, 'dayofweek', 31)
    events2preds = add_cyclic_features(events2preds, 'weekofyear', 31)
    events2preds.drop("Дата создания во внешней системе", axis=1, inplace=True)

    numerical_features = [col for col in events2preds.columns if col not in categorical_features]

    # Удаление строк с NaN в числовых признаках
    events2preds[numerical_features] = events2preds[numerical_features].fillna(events2preds[numerical_features].mean())

    for col in categorical_features:
        events2preds[col] = events2preds[col].astype(str)

    preds = model.predict_proba(events2preds[features])
    events2preds['УНОМ'] = events2preds['УНОМ'].astype(float).astype(int)
    events2preds['preds'] = preds.tolist()

    return events2preds[['УНОМ', 'preds']].set_index('УНОМ')['preds'].to_dict()


def get_predict_for_one(model: CatBoostClassifier, unom: int, date: datetime.datetime, n: int, conn) -> dict:
    agg_data = get_agg_data_one(unom, conn)
    events2preds = pd.DataFrame({
        "УНОМ": [unom] * n,
        "Дата создания во внешней системе": [(date + pd.Timedelta(days=i)) for i in range(n)],
        "month": [date.month] * n,
        "day": [date.day] * n
    })
    odpu = get_odpu_one(unom, date, conn)
    events2preds[ftrs2odpu] = events2preds.apply(lambda x: add_opdu_features(odpu, x), axis=1)

    with open('weather.json', 'r', encoding='utf-8') as file:
        weather = json.load(file)
    events2preds[['weather1', 'weather2']] = events2preds.apply(lambda x: collect_weather(x, weather), axis=1)

    events = get_events_one(unom, date, conn)

    events2preds[feature2events] = events2preds.apply(lambda x: collect_events(x, events), axis=1)
    agg_data['УНОМ'] = agg_data['unom']
    events2preds = events2preds.merge(agg_data[features2aggdata], how='left', on='УНОМ')

    events2preds = extract_datetime_features(events2preds, "Дата создания во внешней системе")
    events2preds = add_cyclic_features(events2preds, 'month', 12)
    events2preds = add_cyclic_features(events2preds, 'hour', 24)
    events2preds = add_cyclic_features(events2preds, 'quarter', 4)
    events2preds = add_cyclic_features(events2preds, 'day', 31)
    events2preds = add_cyclic_features(events2preds, 'dayofweek', 31)
    events2preds = add_cyclic_features(events2preds, 'weekofyear', 31)
    events2preds.drop("Дата создания во внешней системе", axis=1, inplace=True)

    numerical_features = [col for col in events2preds.columns if col not in categorical_features]

    # Удаление строк с NaN в числовых признаках
    events2preds[numerical_features] = events2preds[numerical_features].fillna(events2preds[numerical_features].mean())

    for col in categorical_features:
        events2preds[col] = events2preds[col].astype(str)

    preds = model.predict_proba(events2preds[features])

    return preds.tolist()


ftrs2odpu = [
    'mean_volume1forhour',
    'std_volume1forhour',
    'mean_volume2forhour',
    'std_volume2forhour',
    'mean_q2forhour',
    'std_q2forhour',
    'min_volume1forhour',
    'max_volume1forhour',
    'median_volume1forhour',
    'min_volume2forhour',
    'max_volume2forhour',
    'median_volume2forhour',
    'min_q2forhour',
    'max_q2forhour',
    'median_q2forhour',
    'Потребители',
    'Группа',
    'Центральное отопление(контур)',
    'Ошибки'
]


def add_opdu_features(odpu, row):
    local_odpu = odpu[odpu['UNOM'] == row['УНОМ']]
    curr_time = row['Дата создания во внешней системе']
    local_odpu = local_odpu[local_odpu['Месяц/Год'] < curr_time]
    if len(local_odpu) > 14:
        local_odpu = local_odpu.iloc[-14:]

    for feature in ['volume1forhour', 'volume2forhour', 'q2forhour']:
        row[f'mean_{feature}'] = local_odpu[feature].mean()
        row[f'std_{feature}'] = local_odpu[feature].std()
        row[f'min_{feature}'] = local_odpu[feature].min()
        row[f'max_{feature}'] = local_odpu[feature].max()
        row[f'median_{feature}'] = local_odpu[feature].median()
    if len(local_odpu) > 0:
        row['Потребители'] = local_odpu['Потребители'].iloc[-1]
        row['Группа'] = local_odpu['Группа'].iloc[-1]
        row['Центральное отопление(контур)'] = local_odpu['Центральное отопление(контур)'].iloc[-1]
        row['Ошибки'] = local_odpu['Ошибки'].iloc[-1]
    else:
        row['Потребители'] = None
        row['Группа'] = None
        row['Центральное отопление(контур)'] = None
        row['Ошибки'] = None
    return row[ftrs2odpu]


def get_odpu(date: datetime.datetime, conn) -> pd.DataFrame:  # возвращает таблицу odpu, ОБРЕЗАННУЮ ПО ДАТЕ
    odpu = pd.read_sql(
        f"""
        SELECT
            *
        FROM 
            heating_data
        WHERE
            to_date(month_year, 'DD-MM-YYYY') BETWEEN to_date('{(date - pd.Timedelta(days=14)).strftime("%d-%m-%Y")}', 'DD-MM-YYYY')
            AND to_date('{date.strftime("%d-%m-%Y")}', 'DD-MM-YYYY')
        ;
        """, conn
    )
    odpu.rename(columns={
        'unom': 'UNOM',
        'id_uu': 'ID УУ',
        'id_tu': 'ID ТУ',
        'district': 'Округ',
        'area': 'Район',
        'consumers': 'Потребители',
        'group_type': 'Группа',
        'address': 'Адрес',
        'central_heating_contour': 'Центральное отопление(контур)',
        'meter_brand': 'Марка счетчика ',
        'meter_serial_number': 'Серия/Номер счетчика',
        'date': 'Дата',
        'month_year': 'Месяц/Год',
        'unit': 'Unit',
        'volume_supplied': 'Объём поданого теплоносителя в систему ЦО',
        'volume_returned': 'Объём обратного теплоносителя из системы ЦО',
        'difference_supply_return_mix': 'Разница между подачей и обраткой(Подмес)',
        'difference_supply_return_leak': 'Разница между подачей и обраткой(Утечка)',
        'temperature_supply': 'Температура подачи',
        'temperature_return': 'Температура обратки',
        'meter_operating_hours': 'Наработка часов счётчика',
        'heat_energy_consumption': 'Расход тепловой энергии',
        'errors': 'Ошибки'
    }, inplace=True)
    odpu['Месяц/Год'] = pd.to_datetime(odpu['Месяц/Год'], format='%d-%m-%Y')
    opdu = odpu[(odpu['Месяц/Год'] <= date) &
                (odpu['Месяц/Год'] >= date - pd.Timedelta(days=14))]

    odpu.sort_values(by='Месяц/Год', inplace=True, ignore_index=True)
    odpu['Объём поданого теплоносителя в систему ЦО'] = odpu['Объём поданого теплоносителя в систему ЦО'].astype(float)
    odpu['volume1forhour'] = odpu['Объём поданого теплоносителя в систему ЦО'] / (odpu['Наработка часов счётчика'])
    odpu['volume2forhour'] = odpu['Объём обратного теплоносителя из системы ЦО'] / (odpu['Наработка часов счётчика'])
    odpu['q2forhour'] = odpu['Расход тепловой энергии'].astype(float) / (odpu['Наработка часов счётчика'])

    return odpu


def get_odpu_one(unom: int, date: datetime.datetime, conn):
    odpu = pd.read_sql(
        f"""
        SELECT
            *
        FROM 
            heating_data
        WHERE
            heating_data.unom = {unom}
            AND to_date(month_year, 'DD-MM-YYYY') BETWEEN to_date('{(date - pd.Timedelta(days=14)).strftime("%d-%m-%Y")}', 'DD-MM-YYYY')
            AND to_date('{date.strftime("%d-%m-%Y")}', 'DD-MM-YYYY')
        ;
        """, conn
    )
    odpu.rename(columns={
        'unom': 'UNOM',
        'id_uu': 'ID УУ',
        'id_tu': 'ID ТУ',
        'district': 'Округ',
        'area': 'Район',
        'consumers': 'Потребители',
        'group_type': 'Группа',
        'address': 'Адрес',
        'central_heating_contour': 'Центральное отопление(контур)',
        'meter_brand': 'Марка счетчика ',
        'meter_serial_number': 'Серия/Номер счетчика',
        'date': 'Дата',
        'month_year': 'Месяц/Год',
        'unit': 'Unit',
        'volume_supplied': 'Объём поданого теплоносителя в систему ЦО',
        'volume_returned': 'Объём обратного теплоносителя из системы ЦО',
        'difference_supply_return_mix': 'Разница между подачей и обраткой(Подмес)',
        'difference_supply_return_leak': 'Разница между подачей и обраткой(Утечка)',
        'temperature_supply': 'Температура подачи',
        'temperature_return': 'Температура обратки',
        'meter_operating_hours': 'Наработка часов счётчика',
        'heat_energy_consumption': 'Расход тепловой энергии',
        'errors': 'Ошибки'
    }, inplace=True)
    odpu['Месяц/Год'] = pd.to_datetime(odpu['Месяц/Год'], format='%d-%m-%Y')
    opdu = odpu[(odpu['Месяц/Год'] <= date) &
                (odpu['Месяц/Год'] >= date - pd.Timedelta(days=14))]

    odpu.sort_values(by='Месяц/Год', inplace=True, ignore_index=True)
    odpu['Объём поданого теплоносителя в систему ЦО'] = odpu['Объём поданого теплоносителя в систему ЦО'].astype(float)
    odpu['volume1forhour'] = odpu['Объём поданого теплоносителя в систему ЦО'] / (odpu['Наработка часов счётчика'])
    odpu['volume2forhour'] = odpu['Объём обратного теплоносителя из системы ЦО'] / (odpu['Наработка часов счётчика'])
    odpu['q2forhour'] = odpu['Расход тепловой энергии'].astype(float) / (odpu['Наработка часов счётчика'])

    return odpu


def get_agg_data(conn) -> pd.DataFrame:
    df = pd.read_sql_query(
        """ 
        SELECT *
        FROM buildings
        """, conn
    )
    new_column_names = {
        'external_system_address': 'Адрес из сторонней системы',
        'external_system_id': 'Идентификатор из сторонней системы',
        'bti_address': 'Адрес по БТИ',
        'unom': 'unom',
        'district': 'Округ',
        'area': 'Район',
        'project_series': 'Серии проектов',
        'number_of_floors': 'Количество этажей',
        'number_of_entrances': 'Количество подъездов',
        'number_of_apartments': 'Количество квартир',
        'total_area': 'Общая площадь',
        'total_residential_area': 'Общая площадь жилых помещений',
        'total_non_residential_area': 'Общая площадь нежилых помещений',
        'wear_and_tear_bti': 'Износ объекта (по БТИ)',
        'wall_materials': 'Материалы стен',
        'emergency_status': 'Признак аварийности здания',
        'number_of_passenger_elevators': 'Количество пассажирских лифтов',
        'number_of_freight_elevators': 'Количество грузопассажирских лифтов',
        'roof_cleaning_priority': 'Очередность уборки кровли',
        'roof_materials': 'Материалы кровли по БТИ',
        'housing_fund_types': 'Типы жилищного фонда',
        'mkd_statuses': 'Статусы МКД',
        'consumers': 'Потребители',
        'group_type': 'Группа',
        'central_heating': 'Центральное отопление(контур)',
        'meter_brand': 'Марка счетчика ',
        'meter_serial_number': 'Серия/Номер счетчика',
        'id_uu': 'ID УУ',
        'full_address': 'Полный адрес',
        'ods_number': '№ ОДС',
        'ods_address': 'Адрес ОДС',
        'ctp': 'ЦТП',
        'serial_number': '№ п/п',
        'city': 'Город',
        'administrative_district': 'Административный округ',
        'municipal_district': 'Муниципальный округ',
        'locality': 'Населенный пункт',
        'street': 'Улица',
        'house_number_type': 'Тип номера дом',
        'house_number': 'Номер дома',
        'building_number': 'Номер корпуса',
        'structure_number_type': 'Тип номера строения/сооружения',
        'structure_number': 'Номер строения',
        'unad': 'UNAD',
        'material': 'Материал',
        'purpose': 'Назначение',
        'class': 'Класс',
        'type': 'Тип',
        'sign': 'Признак',
        'global_id': 'global_id',
        'obj_type': 'OBJ_TYPE',
        'address_x': 'ADDRESS_x',
        'municipal_district_1': 'Муниципальный округ',
        'planning_element_name': 'Наименование элемента планировочной структуры или улично-дорожной сети',
        'house_ownership_number_type': 'Тип номера дома, владения, участка',
        'intra_city_area': 'Внутригородская территория',
        'adm_area': 'ADM_AREA',
        'district_1': 'DISTRICT',
        'nreg': 'NREG',
        'dreg': 'DREG',
        'n_fias': 'N_FIAS',
        'd_fias': 'D_FIAS',
        'kad_n': 'KAD_N',
        'kad_zu': 'KAD_ZU',
        'kladr': 'KLADR',
        'tdoc': 'TDOC',
        'ndoc': 'NDOC',
        'ddoc': 'DDOC',
        'adr_type': 'ADR_TYPE',
        'vid': 'VID',
        'sostad': 'SOSTAD',
        'status': 'STATUS',
        'geo_data': 'geoData',
        'geo_data_center': 'geodata_center',
        'id_ods': 'ID ODS',
        'phone_number': 'PHONE_NUMBER'
    }

    # Переименование столбцов
    df.rename(columns=new_column_names, inplace=True)
    return df


def get_agg_data_one(unom: int, conn) -> pd.DataFrame:
    df = pd.read_sql_query(
        f""" 
        SELECT *
        FROM buildings
        WHERE buildings.unom = {unom}
        """, conn
    )
    new_column_names = {
        'external_system_address': 'Адрес из сторонней системы',
        'external_system_id': 'Идентификатор из сторонней системы',
        'bti_address': 'Адрес по БТИ',
        'unom': 'unom',
        'district': 'Округ',
        'area': 'Район',
        'project_series': 'Серии проектов',
        'number_of_floors': 'Количество этажей',
        'number_of_entrances': 'Количество подъездов',
        'number_of_apartments': 'Количество квартир',
        'total_area': 'Общая площадь',
        'total_residential_area': 'Общая площадь жилых помещений',
        'total_non_residential_area': 'Общая площадь нежилых помещений',
        'wear_and_tear_bti': 'Износ объекта (по БТИ)',
        'wall_materials': 'Материалы стен',
        'emergency_status': 'Признак аварийности здания',
        'number_of_passenger_elevators': 'Количество пассажирских лифтов',
        'number_of_freight_elevators': 'Количество грузопассажирских лифтов',
        'roof_cleaning_priority': 'Очередность уборки кровли',
        'roof_materials': 'Материалы кровли по БТИ',
        'housing_fund_types': 'Типы жилищного фонда',
        'mkd_statuses': 'Статусы МКД',
        'consumers': 'Потребители',
        'group_type': 'Группа',
        'central_heating': 'Центральное отопление(контур)',
        'meter_brand': 'Марка счетчика ',
        'meter_serial_number': 'Серия/Номер счетчика',
        'id_uu': 'ID УУ',
        'full_address': 'Полный адрес',
        'ods_number': '№ ОДС',
        'ods_address': 'Адрес ОДС',
        'ctp': 'ЦТП',
        'serial_number': '№ п/п',
        'city': 'Город',
        'administrative_district': 'Административный округ',
        'municipal_district': 'Муниципальный округ',
        'locality': 'Населенный пункт',
        'street': 'Улица',
        'house_number_type': 'Тип номера дом',
        'house_number': 'Номер дома',
        'building_number': 'Номер корпуса',
        'structure_number_type': 'Тип номера строения/сооружения',
        'structure_number': 'Номер строения',
        'unad': 'UNAD',
        'material': 'Материал',
        'purpose': 'Назначение',
        'class': 'Класс',
        'type': 'Тип',
        'sign': 'Признак',
        'global_id': 'global_id',
        'obj_type': 'OBJ_TYPE',
        'address_x': 'ADDRESS_x',
        'municipal_district_1': 'Муниципальный округ',
        'planning_element_name': 'Наименование элемента планировочной структуры или улично-дорожной сети',
        'house_ownership_number_type': 'Тип номера дома, владения, участка',
        'intra_city_area': 'Внутригородская территория',
        'adm_area': 'ADM_AREA',
        'district_1': 'DISTRICT',
        'nreg': 'NREG',
        'dreg': 'DREG',
        'n_fias': 'N_FIAS',
        'd_fias': 'D_FIAS',
        'kad_n': 'KAD_N',
        'kad_zu': 'KAD_ZU',
        'kladr': 'KLADR',
        'tdoc': 'TDOC',
        'ndoc': 'NDOC',
        'ddoc': 'DDOC',
        'adr_type': 'ADR_TYPE',
        'vid': 'VID',
        'sostad': 'SOSTAD',
        'status': 'STATUS',
        'geo_data': 'geoData',
        'geo_data_center': 'geodata_center',
        'id_ods': 'ID ODS',
        'phone_number': 'PHONE_NUMBER'
    }

    # Переименование столбцов
    df.rename(columns=new_column_names, inplace=True)
    return df


feature2events = [
    'Давление не в норме_count',
    'T < min_count',
    'T > max_count',
    'Утечка_count',
    'month1_count',
    'month2_count',
    'month3_count',
    'month4_count',
    'month10_count',
    'month11_count',
    'month12_count'
]

new_event_names = [
    'Давление не в норме',
    'T < min',
    'T > max',
    'Утечка'
]


def collect_events(row, events):
    local_events = events[events['УНОМ'] == row['УНОМ']]
    curr_time = row['Дата создания во внешней системе']
    local_events = local_events[local_events['Дата создания во внешней системе'] > curr_time]
    grpb = local_events.groupby('Наименование').count()['УНОМ']
    for event_type in new_event_names:
        if event_type in grpb:
            row[f'{event_type}_count'] = grpb[event_type]
        else:
            row[f'{event_type}_count'] = 0

    grpb = local_events.groupby('month').count()['Наименование']
    for month_num in [1, 2, 3, 4, 10, 11, 12]:
        if month_num in grpb:
            row[f"month{month_num}_count"] = grpb[month_num]
        else:
            row[f"month{month_num}_count"] = 0

    return row[feature2events]


num2month = {
    10: "october",
    11: "november",
    12: "december",
    1: "january",
    2: "february",
    3: "march",
    4: "april",
    5: "may",
    6: "june",
    7: "july",
    8: "august",
    9: "september"
}


def collect_weather(row, weather):
    mon = num2month[row.month]
    day = "{:02d}".format(row.day)
    row['weather1'], row['weather2'] = weather[mon][day]
    return row[['weather1', 'weather2']]


def get_events(date, conn) -> pd.DataFrame:
    events = pd.read_sql(
        f"""
        SELECT *
        FROM events
        WHERE 
            events.creation_date <= '{date.strftime("%Y-%m-%d")}'
            AND events.creation_date >= '2023-10-01'
        """, conn
    )
    events.rename(columns={
        'name': 'Наименование',
        'source': 'Источник',
        'creation_date': 'Дата создания во внешней системе',
        'closure_date': 'Дата закрытия',
        'district': 'Округ',
        'unom': 'УНОМ',
        'address': 'Адрес',
        'event_completion_date': 'Дата и время завершения события'
    }, inplace=True)

    eventNames2labels = {
        "P1 <= 0": "Давление не в норме",
        "P2 <= 0": "Давление не в норме",
        "T1 > max": "T > max",
        "T1 < min": "T < min",
        "Недостаточная температура подачи в центральном отоплении (Недотоп)": "T < min",
        "Превышение температуры подачи в центральном отоплении (Перетоп)": "T > max",
        "Утечка теплоносителя": "Утечка",
        "Течь в системе отопления": "Утечка",
        "Температура в квартире ниже нормативной": "T < min",
        "Отсутствие отопления в доме": "T < min",
        "Сильная течь в системе отопления": "Утечка",
        "Температура в помещении общего пользования ниже нормативной": "T < min",
        "Аварийная протечка труб в подъезде": "Утечка",
        "Протечка труб в подъезде": "Утечка",
        "Температура в помещении общего пользования ниже нормативной": "T < min",
        "Отсутствие отопления в доме": "T < min",
        "Температура в квартире ниже нормативной": "T < min",
        "Течь в системе отопления": "Утечка",
        "Сильная течь в системе отопления": "Утечка",

    }

    event_names = list(eventNames2labels.keys())
    events = events[events['Наименование'].isin(event_names)]
    events['Наименование'] = events['Наименование'].apply(lambda x: eventNames2labels[x])
    events['Дата создания во внешней системе'] = pd.to_datetime(events['Дата создания во внешней системе'])
    events.sort_values(by='Дата создания во внешней системе', inplace=True, ignore_index=True)
    events['month'] = events['Дата создания во внешней системе'].apply(lambda x: x.month)
    events['day'] = events['Дата создания во внешней системе'].apply(lambda x: x.day)
    events = events[['Наименование', 'Источник', 'Дата создания во внешней системе', 'УНОМ', 'month', 'day']]

    return events


def get_events_one(unom: int, date: datetime.datetime, conn) -> pd.DataFrame:
    events = pd.read_sql(
        f"""
        SELECT *
        FROM events
        WHERE 
            events.creation_date <= '{date.strftime("%Y-%m-%d")}'
            AND events.creation_date >= '2023-10-01'
            AND unom = {unom}
        """, conn
    )
    events.rename(columns={
        'name': 'Наименование',
        'source': 'Источник',
        'creation_date': 'Дата создания во внешней системе',
        'closure_date': 'Дата закрытия',
        'district': 'Округ',
        'unom': 'УНОМ',
        'address': 'Адрес',
        'event_completion_date': 'Дата и время завершения события'
    }, inplace=True)

    eventNames2labels = {
        "P1 <= 0": "Давление не в норме",
        "P2 <= 0": "Давление не в норме",
        "T1 > max": "T > max",
        "T1 < min": "T < min",
        "Недостаточная температура подачи в центральном отоплении (Недотоп)": "T < min",
        "Превышение температуры подачи в центральном отоплении (Перетоп)": "T > max",
        "Утечка теплоносителя": "Утечка",
        "Течь в системе отопления": "Утечка",
        "Температура в квартире ниже нормативной": "T < min",
        "Отсутствие отопления в доме": "T < min",
        "Сильная течь в системе отопления": "Утечка",
        "Температура в помещении общего пользования ниже нормативной": "T < min",
        "Аварийная протечка труб в подъезде": "Утечка",
        "Протечка труб в подъезде": "Утечка",
        "Температура в помещении общего пользования ниже нормативной": "T < min",
        "Отсутствие отопления в доме": "T < min",
        "Температура в квартире ниже нормативной": "T < min",
        "Течь в системе отопления": "Утечка",
        "Сильная течь в системе отопления": "Утечка",

    }

    event_names = list(eventNames2labels.keys())
    events = events[events['Наименование'].isin(event_names)]
    events['Наименование'] = events['Наименование'].apply(lambda x: eventNames2labels[x])
    events['Дата создания во внешней системе'] = pd.to_datetime(events['Дата создания во внешней системе'])
    events.sort_values(by='Дата создания во внешней системе', inplace=True, ignore_index=True)
    events['month'] = events['Дата создания во внешней системе'].apply(lambda x: x.month)
    events['day'] = events['Дата создания во внешней системе'].apply(lambda x: x.day)
    events = events[['Наименование', 'Источник', 'Дата создания во внешней системе', 'УНОМ', 'month', 'day']]

    return events


def extract_datetime_features(df, date_col):
    df['year'] = df[date_col].dt.year
    df['month'] = df[date_col].dt.month
    df['day'] = df[date_col].dt.day
    df['hour'] = df[date_col].dt.hour
    df['dayofweek'] = df[date_col].dt.dayofweek
    df['weekofyear'] = df[date_col].dt.isocalendar().week
    df['quarter'] = df[date_col].dt.quarter
    df['is_month_start'] = df[date_col].dt.is_month_start
    df['is_month_end'] = df[date_col].dt.is_month_end
    return df


def add_cyclic_features(df, col, max_val):
    df[col + '_sin'] = np.sin(2 * np.pi * df[col] / max_val)
    df[col + '_cos'] = np.cos(2 * np.pi * df[col] / max_val)
    return df

class CatBoostModel:
    def __init__(self, data, type_description_dict, material_parameters_dict, model_path='catboost.cbm'):
        """
        Инициализация класса CatBoostModel.

        Args:
            data (pd.DataFrame): Исходные данные.
            type_description_dict (dict): Словарь с описанием типов материалов.
            material_parameters_dict (dict): Словарь с параметрами материалов.
            model_path (str): Путь к сохраненной модели CatBoost.
        """
        self.data = data
        self.type_description_dict = type_description_dict
        self.material_parameters_dict = material_parameters_dict
        self.model_path = model_path
        self.model = CatBoostRegressor().load_model(self.model_path)

    def get_data_by_unum(self, unom) -> dict:
        """
        Получение данных для данного 'unom' из соответствующих словарей.

        Args:
            unom (float): 'unom' дома.
            conn - соединение с базой данных

        Returns:
            dict: Словарь с данными для указанного 'unom'.
        """
        try:
            # Подключение к базе данных
            conn = connect_to_db()
            selected_columns = ["total_area", "number_of_floors", "wall_materials"]
            query = f"""
            SELECT {', '.join(selected_columns)}
            FROM buildings
            WHERE unom = %s;
            """
            cursor = conn.cursor()
            cursor.execute(query, (unom,))
            result = cursor.fetchone()
            if result:
                # Получаем названия столбцов из описания курсора
                column_names = [desc[0] for desc in cursor.description]

                # Создаем словарь для хранения данных
                data_dict = {}
                for i, name in enumerate(column_names):
                    data_dict[name] = result[i]

                # Проверяем наличие nan или None в словаре
                # has_nan_or_none = any(value is None or value == '' or value=='nan' for value in data_dict.values())

                # if has_nan_or_none:
                #     print("В данных присутствуют значения nan или None")
                #     print(None)

                new_dict = {}
                new_keys = ["Общая площадь", "Количество этажей", "Материалы стен"]
                for old_key, new_key in zip(data_dict.keys(), new_keys):
                    new_dict[new_key] = data_dict[old_key]

                temp_data = new_dict
                # print(temp_data)

                S = temp_data['Общая площадь']
                if str(S) == 'nan': S = 6500
                if not S: S = 6500

                # print("Общая площадь",S)
                N = temp_data['Количество этажей']
                if not N: N = 9
                if str(N) == 'nan': N = 9


                # print("Количество этажей", N)
                d = 0.3
                material = self.type_description_dict.get(temp_data['Материалы стен'], 'Железобетон')
                L, c1, ro1 = self.material_parameters_dict[material]

                return {
                    'S': S,
                    'N': N,
                    'd': d,
                    'L': L,
                    'c1': c1,
                    'ro1': ro1
                }
            else:
                print("Ошибка в данных")
                return {'S': 1426.6,
                        'N': 4.0,
                        'd': 0.3,
                        'L': 0.67,
                        'c1': 840,
                        'ro1': 1750
                        }

        except Exception as e:
                print(f"2Ошибка при подключении к базе данных: {e}")
                return None


    def prepare_one_data_sample(self, unom, t_in, t_outside):
        """
        Подготаливает данные для одного образца для модели на основе входных параметров.

        Args:
            unom (float): 'unom' дома.
            t_in (float): Текущая температура внутри для данного 'unom'.
            t_outside (dict): Словарь с температурами через 5, 10, ..., 30 часов.

        Returns:
            dict: Словарь с подготовленными данными для модели.
        """
        unom_dict = self.get_data_by_unum(unom)

        h = 3  # Средняя высота одного этажа
        # print(unom_dict)
        P = 4 * math.sqrt(unom_dict['S'] / unom_dict['N'])  # Расчет периметра
        V = unom_dict['S'] * h  # Расчет объема
        alpha = unom_dict['L'] / unom_dict['d']  # Расчет коэффициента альфа
        A = P * unom_dict['N'] * h  # Расчет параметра A

        return {
            'unom': unom,
            't_inside': t_in,
            'c1': unom_dict['c1'],
            'ro1': unom_dict['ro1'],
            'V': V,
            'alpha': alpha,
            'A': A,
            't_in_5_hours': t_outside['t_in_5_hours'],
            't_in_10_hours': t_outside['t_in_10_hours'],
            't_in_15_hours': t_outside['t_in_15_hours'],
            't_in_20_hours': t_outside['t_in_20_hours'],
            't_in_25_hours': t_outside['t_in_25_hours'],
            't_in_30_hours': t_outside['t_in_30_hours'],
        }

    def prepare_data_for_catboost(self, unoms, t_inside, t_outside):
        """
        Готовит данные для модели CatBoost на основе входных данных.

        Args:
            unoms (list): Список значений 'unom' для которых производится расчет.
            t_inside (list): Список текущих температур для каждого 'unom'.
            t_outside (dict): Словарь, где ключи - 't_in_5_hours', 't_in_10_hours', ..., 't_in_30_hours',
                              а значения - соответствующие температуры через 5, 10, ..., 30 часов.

        Returns:
            pd.DataFrame: DataFrame, содержащий данные, подготовленные для модели CatBoost.
        """
        data_for_catboost = [self.prepare_one_data_sample(unom, t_in, t_outside) for unom, t_in in zip(unoms, t_inside)]
        return pd.DataFrame(data_for_catboost)

    def get_catboost_predictions(self, data_for_catboost):
        """
        Получает прогнозы с использованием модели CatBoost и возвращает их в виде словаря.

        Args:
            data_for_catboost (pd.DataFrame): Входные данные для модели CatBoost.

        Returns:
            dict: Словарь, {unom: hours_until_cooling}, где hours_until_cooling - часы до остывания дома.
        """
        data_for_catboost['hours_until_cooling'] = self.model.predict(data_for_catboost).astype('int64')
        return data_for_catboost.set_index('unom')['hours_until_cooling'].to_dict()

    def complex_custom_ranking(self, unom, hours):
        """
        Рассчитывает комплексный приоритет для здания на основе различных параметров.

        Аргументы:
            unom (int): Уникальный идентификатор здания.
            hours (int): Количество часов до остывания здания.

        Возвращает:
            int: Рассчитанный приоритет здания, где 1 - наивысший приоритет.

        Описание:
            Метод рассчитывает приоритет здания на основе следующих параметров:
            - Категория здания (жилое, социальное, промышленное)
            - Класс энергоэффективности здания
            - Режим работы здания

            Приоритет рассчитывается с учетом веса этих параметров и нормализуется в диапазоне, где 1 означает наивысший приоритет.
        """

        try:
            # Подключение к базе данных
            conn = connect_to_db()
            selected_columns = ["work_hours", "energy_efficiency_class", "purpose"]
            query = f"""
            SELECT {', '.join(selected_columns)}
            FROM buildings
            WHERE unom = %s;
            """
            cursor = conn.cursor()
            cursor.execute(query, (int(unom),))
            print("bruh")
            result = cursor.fetchone()
            if result:
                # Получаем названия столбцов из описания курсора
                column_names = [desc[0] for desc in cursor.description]

                # Создаем словарь для хранения данных
                data_dict = {}
                for i, name in enumerate(column_names):
                    data_dict[name] = result[i]

                # Проверяем наличие nan или None в словаре
                # has_nan_or_none = any(value is None or value == '' or value=='nan' for value in data_dict.values())

                # if has_nan_or_none:
                #     print("В данных присутствуют значения nan или None")
                #     print(None)

                new_dict = {}
                new_keys = ["Режим работы", "Класс энергоэффективности здания", "Назначение"]
                for old_key, new_key in zip(data_dict.keys(), new_keys):
                    new_dict[new_key] = data_dict[old_key]

                apartment_tags = ['многоквартирный дом', 'блокированный жилой дом', 'общежитие', 'спальный корпус', 'гараж', 'дом ребенка', 'интернат', 'гостиница']
                social_tags = ['школа', 'библиотека', 'музей', 'детский сад', 'колледж', 'больница', 'родильный дом', 'поликлиника', 'ясли-сад', 'медучилище', 'дом детского творчества', 'музыкальная школа', 'школа-интернат', 'гимназия', 'лечебный корпус', 'санаторий', 'центр реабилитации', 'спецшкола', 'училище', 'лечебное', 'учебное', 'учебно-производственный комбинат', 'культурно-просветительное', 'техническое училище', 'техникум', 'школа-сад', 'детские ясли', 'станция скорой помощи', 'спортивная школа', 'наркологический диспансер', 'профтехучилище', 'спортивный клуб', 'лаборатория', 'детский санаторий', 'диспансер', 'дворец пионеров', 'детсад-ясли', 'детский дом культуры', 'ясли', 'физкультурно-оздоровительный комплекс', 'клуб', 'бассейн и спортзал', 'спортивный корпус', 'детское дошкольное учреждение', 'подстанция скорой помощи', 'блок-пристройка начальных классов', 'спортивное', 'кафе', 'столовая', 'центр обслуживания']
                industrial_tags = ['трансформаторная подстанция', 'нежилое', 'выставочный павильон', 'кухня клиническая', 'хозблок', 'овощехранилище', 'учреждение', 'хирургический корпус', 'морг', 'пищеблок', 'учебно-воспитателный комбинат', 'учреждение,мастерские', 'дезинфекционная камера', 'отделение судебно-медицинской экспертизы', 'пункт охраны', 'учебный корпус', 'плавательный бассейн', 'хранилище', 'административное', 'научное', 'архив', 'учебно-воспитательное', 'терапевтический корпус', 'учебное', 'административно-бытовой']

                energy_efficiency = new_dict['Класс энергоэффективности здания']
                energy_efficiency_mapping = {'A++': 2, 'A+': 3, 'A': 4, 'B': 5, 'C': 6, 'D': 7, 'E': 8, 'F': 9, 'G': 10}  # Словарь для сопоставления уровня энергоэффективности с числовым значением
                efficiency_weight = energy_efficiency_mapping.get(energy_efficiency, 1)  # По умолчанию, если энергоэффективность неизвестна или некорректна

                # Определение весов категорий
                purpose_weight = new_dict.get(new_dict['Назначение'], "многоквартирный дом")
                if purpose_weight in social_tags:
                    weight = 3
                elif purpose_weight in industrial_tags:
                    weight = 2
                else:
                    weight = 1

                # Определение весов режима работы

                working_time = new_dict['Режим работы']
                working_time_mapping = {'Круглосуточно': 3, '9:00 - 21:00': 2, '9:00 – 18:00': 1}  # Словарь для сопоставления уровня энергоэффективности с числовым значением
                working_weight = working_time_mapping.get(working_time, 1)  # По умолчанию, если энергоэффективность неизвестна или некорректна

                if hours <= 2:
                    # приоритет максимальный (1)
                    return 1
                else:
                    # Формула для расчета приоритета
                    return 4 - ((weight + efficiency_weight + working_weight) / hours)
            else:
                return None

        except Exception as e:
                print(f"3Ошибка при подключении к базе данных: {e}")
                return None



    def get_final_ranking(self, data_from_request):
        """
        Рассчитывает окончательный рейтинг зданий на основе данных о часах до остывания.

        Аргументы:
            data_from_request (dict): Словарь, где ключи - 'unom' зданий,
                                      а значения - часы до остывания здания.

        Возвращает:
            pd.DataFrame: DataFrame, содержащий отсортированные данные по приоритету,
                          включающий столбцы 'unom', 'hours' и 'Rank'.
                          Значения в столбце 'Rank' нормализованы в диапазоне от 1 до 3,
                          где 1 - максимальный приоритет.

        Пример:
            >>> data_from_request = {
            ...     101: 5,
            ...     102: 2,
            ...     103: 8,
            ... }
            >>> model = CatBoostModel(data, type_description_dict, material_parameters_dict, model_path)
            >>> df_ranking = model.get_final_ranking(data_from_request)
            >>> print(df_ranking)
               unom  hours  Rank
            0   102      2     1
            1   101      5     2
            2   103      8     3
        """

        df = pd.DataFrame.from_dict(data_from_request, orient='index').reset_index()
        df.columns = ['unom', 'hours']

        # Применение функции расчета приоритета к каждому объекту
        df['Rank'] = df.apply(lambda row: self.complex_custom_ranking(row['unom'], row['hours']), axis=1)

        # Нормализация приоритета к диапазону от 1 до 3
        df['Rank'] = df['Rank'].apply(lambda x: max(1, min(3, round(x))))

        # Сортировка по приоритету
        df_sorted = df.sort_values(by='Rank', ascending=True)

        return df_sorted

def get_current_temperature():
    """
    Функция для получения прогноза погоды от Яндекс.Погоды по координатам.
    :param lat: Широта
    :param lon: Долгота
    :return: Прогноз погоды
    """
    url = f'https://api.weather.yandex.ru/v2/forecast?lat=55.787715&lon=37.775631'
    headers = {'X-Yandex-Weather-Key': "83f2c69f-542f-4a2a-b1dc-b32b2d01e7ac"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()["fact"]["temp"]
    else:
        print(f"Ошибка при запросе: {response.status_code}")
        return None


def get_future_temperature():
    """
    Функция для получения прогноза погоды от Яндекс.Погоды по координатам.
    :param lat: Широта
    :param lon: Долгота
    :return: Прогноз погоды
    """
    # Получаем текущую дату и время
    now = int(get_current_temperature())

    url = f'https://api.weather.yandex.ru/v2/forecast?lat=55.787715&lon=37.775631'
    headers = {'X-Yandex-Weather-Key': "83f2c69f-542f-4a2a-b1dc-b32b2d01e7ac"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return {
            't_in_5_hours': now,
            't_in_10_hours': now,
            't_in_15_hours': now,
            't_in_20_hours': now,
            't_in_25_hours': now,
            't_in_30_hours': now
        }
    else:
        print(f"Ошибка при запросе: {response.status_code}")
        return None


def connect_to_db():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        print("Подключение к базе данных успешно установлено")
        return conn
    except Exception as e:
        print(f"1Ошибка при подключении к базе данных: {e}")
        return None


def read_data_from_db(conn):
    query = "SELECT * FROM buildings;"  # Замените 'buildings' на название вашей таблицы
    try:
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return None

@app.post("/calc_cooldown/")
async def calc_cooldown(unoms: List[int]):
        """
        Ручка для получение ранжированного списка остывающих объектов

        Аргументы:
            unoms (list): Массив УНОМов

        Возвращает:
            dict: словарь, содержащий отсортированные данные по приоритету,
                          включающий столбцы 'unom', 'hours' и 'Rank'.
                          Значения в столбце 'Rank' нормализованы в диапазоне от 1 до 3,
                          где 1 - максимальный приоритет.
        """
        unoms = [int(unom) for unom in unoms]
        conn = connect_to_db()
        if not conn:
            raise HTTPException(status_code=500, detail="Не удалось подключиться к базе данных")

        try:
            # Считываем данные в DataFrame
            database = read_data_from_db(conn)

            if database is None:
                raise HTTPException(status_code=500, detail="Ошибка при считывании данных из базы данных")

            t_inside = [get_current_temperature()] * len(unoms)
            t_outside = get_future_temperature()

            # Получаем предсказания
            catboost_model = CatBoostModel(database, type_description_dict, material_parameters_dict, model_path='catboost.cbm')
            data_for_catboost = catboost_model.prepare_data_for_catboost(unoms, t_inside, t_outside)
            catboost_predictions = catboost_model.get_catboost_predictions(data_for_catboost)
            df_sorted = catboost_model.get_final_ranking(catboost_predictions)

            return df_sorted.to_dict(orient='records')
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            conn.close()


type_description_file_path = "type_descriptions.json"
material_parameters_file_path = "material_parameters.json"

with open(type_description_file_path, 'r', encoding='utf-8') as file:
    type_description_dict = json.load(file)

with open(material_parameters_file_path, 'r', encoding='utf-8') as file:
    material_parameters_dict = json.load(file)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
