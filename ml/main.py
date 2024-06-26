import math

import pandas as pd
import datetime
import json
import requests

from catboost import CatBoostClassifier, CatBoostRegressor
import numpy as np
import psycopg2

from fastapi import FastAPI, HTTPException, Request, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import warnings

from jwt import ExpiredSignatureError, decode as jwt_decode, exceptions as jwt_exceptions

from typing import List

import os

from starlette.middleware.base import BaseHTTPMiddleware

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_PORT = os.getenv('DB_PORT')
DB_HOST = os.getenv('DB_HOST')

TIME_OUT = 20000000000  # milliseconds

warnings.filterwarnings("ignore")

app = FastAPI()

model = CatBoostClassifier()
model.load_model('./models/model_task1')


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


# async def authorization_middleware(request: Request, call_next):
#     if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
#         return await call_next(request)
#
#     auth = request.headers.get("Authorization")
#     if not auth or "Bearer" not in auth:
#         return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "no bearer provided in authorization"})
#
#     jwt_token = auth.split(" ")[1]
#
#     try:
#         is_accessed = authorize(jwt_token)
#     except Exception as e:
#         return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "error on parsing JWT"})
#
#     if not is_accessed:
#         return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "error on authorizing access JWT"})
#
#     response = await call_next(request)
#     return response


class AuthorizationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        auth = request.headers.get("Authorization")
        if not auth or "Bearer" not in auth:
            return JSONResponse(status_code=401, content={"detail": "no bearer provided in authorization"})

        jwt_token = auth.split(" ")[1]

        try:
            is_accessed = authorize(jwt_token)
        except Exception as e:
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "error on parsing JWT"})

        if not is_accessed:
            return JSONResponse(status_code=status.HTTP_403_FORBIDDEN,
                                content={"detail": "error on authorizing access JWT"})

        response = await call_next(request)
        return response


# Add the authorization middleware first
app.add_middleware(AuthorizationMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/predict_all/")
async def predict_all(date: datetime.datetime):
    """
    Описание
    Получение предсказаний аварийных событий по всем объектам из таблицы buildings за определенную дату (день)

    Входные данные

    date: string формата datetime (2024-04-01T00:00:00)

    Результат
    {
      unom: [prob'T < min', prob'T > max', prob'Давление не в норме', prob'ОК', prob'Утечка']
    }
    unom - УНОМ объекта, string
    prob'T < min', prob'T > max', prob'Давление не в норме', prob'ОК', prob'Утечка' - вероятности каждого из событий, float.

    """
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
async def predict_one(unom: int, date: datetime.datetime, n: int, date_start: datetime.datetime,
                      date_end: datetime.datetime):
    """
    Описание
    Получение предсказаний аварийных событий для одного УНОМа, а также сводки данных по заданному промежутку времени для данного УНОМа

    Входные данные

    unom: integer - УНОМ объекта предсказания
    date: string формата datetime (2024-04-01T00:00:00)
    n: integer - количество дней для прогноза (будут возвращены прогнозы от 0 до n-1 дня)
    date_start: string datetime - начало среза данных для статистик
    date_end: string datetime - конец среза данных для статистик

    Результат
    {
      “predict”: {
    “dd-MM-YYYY”: [prob'T < min', prob'T > max', prob'Давление не в норме', prob'ОК',      prob'Утечка']
      },
      “incidents_count”: {
    “{incident_name}”: incident_count
    },
    “odpu_plot”: {
      “volume1”: {“dd-MM-YYYY”: value},
      “volume2”: {“dd-MM-YYYY”: value},
      “q2”: {“dd-MM-YYYY”: value},
      “difference_supply_return_mix_all”: {“dd-MM-YYYY”: value},
      “difference_supply_return_leak_all”: {“dd-MM-YYYY”: value},
      “temperature_supply_all”: {“dd-MM-YYYY”: value},
      “temperature_return_all”: {“dd-MM-YYYY”: value}
    }
    }
    predict - словарь с ключем - датой, значением - предсказанием за эту дату
    prob'T < min', prob'T > max', prob'Давление не в норме', prob'ОК', prob'Утечка' - вероятности каждого из событий, float.
    incidents_count - количество инцидентов каждого типа за данный промежуток от date_start до date_end
    odpu_plot - словарь со значениями показателей с ОДПУ:

    difference_supply_return_leak_all - Разница между подачей и обраткой(Утечка)
    difference_supply_return_mix_all'- Разница между подачей и обраткой(Подмес)
    q2 - расход тепловой энергии
    temperature_return_all - Температура обратки
    temperature_supply_all - Температура подачи
    volume1 - Объём поданого теплоносителя в систему ЦО
    volume2  - Объём обратного теплоносителя из системы ЦО

    """
    try:
        conn = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,  # локальный хост
            port="5432",  # стандартный порт PostgreSQL
            database=DB_NAME
        )

        # Получаем предсказания
        preds = get_predict_for_one(model, unom, date, n, date_start, date_end, conn)

        return preds

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        conn.close()


@app.get("/get_stats/")
async def get_stats(date: datetime.datetime):
    """
    Получает статистические данные на основе указанной даты.

    Аргументы:
        date (datetime.datetime): Дата, для которой необходимо получить статистические данные.

    Возвращает:
        dict: Структурированные статистические данные, включая количество событий, связанных с управлением теплом,
              количество завершённых и текущих задач, данные о погоде и количество объектов без событий.

    Описание:
        - Устанавливает соединение с базой данных PostgreSQL.
        - Вызывает функцию get_stats_from_bd для извлечения данных о событиях и других статистических показателях.
        - Возвращает ответ в формате JSON с данными о количестве событий, завершённых и текущих задачах,
          погодных условиях и количестве объектов без событий.
    """
    try:
        conn = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,  # локальный хост
            port="5432",  # стандартный порт PostgreSQL
            database=DB_NAME
        )

        # Получаем предсказания
        ans = get_stats_from_bd(date, conn)

        return ans

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
    """Получает предсказания для всех уникальных объектов.

    Аргументы:
        model (CatBoostClassifier): Обученная модель CatBoost.
        date (datetime.datetime): Дата, на основе которой строятся предсказания.
        conn: Соединение с базой данных PostgreSQL.

    Возвращает:
        dict: Словарь, где ключ - уникальный объект (УНОМ), значение - предсказания модели.
    """
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

    with open('./configs/weather.json', 'r', encoding='utf-8') as file:
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
    events2preds.replace('', np.nan, inplace=True)
    events2preds[numerical_features] = events2preds[numerical_features].astype(float)
    events2preds[numerical_features] = events2preds[numerical_features].fillna(events2preds[numerical_features].mean())

    for col in categorical_features:
        events2preds[col] = events2preds[col].astype(str)

    preds = model.predict_proba(events2preds[features])
    events2preds['УНОМ'] = events2preds['УНОМ'].astype(float).astype(int)
    events2preds['preds'] = preds.tolist()

    return events2preds[['УНОМ', 'preds']].set_index('УНОМ')['preds'].to_dict()


def get_predict_for_one(model: CatBoostClassifier, unom: int, date: datetime.datetime, n: int, date_start, date_end,
                        conn) -> dict:
    """
    Получает предсказание для одного объекта на основе модели CatBoost.

    Аргументы:
        model (CatBoostClassifier): Модель CatBoost для предсказаний.
        unom (int): Уникальный номер объекта.
        date (datetime.datetime): Дата для создания предсказания.
        n (int): Количество последних записей для использования.
        conn: Соединение с базой данных PostgreSQL.

    Возвращает:
        dict: Словарь с предсказаниями, где ключ - УНОМ, значение - предсказание.

    """
    agg_data = get_agg_data_one(unom, conn)
    events2preds = pd.DataFrame({
        "УНОМ": [unom] * n,
        "Дата создания во внешней системе": [(date + pd.Timedelta(days=i)) for i in range(n)],
        "month": [date.month] * n,
        "day": [date.day] * n
    })
    odpu = get_odpu_one(unom, date, conn)
    events2preds[ftrs2odpu] = events2preds.apply(lambda x: add_opdu_features(odpu, x), axis=1)

    with open('./configs/weather.json', 'r', encoding='utf-8') as file:
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

    ans = events2preds[['Дата создания во внешней системе']]
    events2preds.drop("Дата создания во внешней системе", axis=1, inplace=True)
    numerical_features = [col for col in events2preds.columns if col not in categorical_features]
    # Удаление строк с NaN в числовых признаках
    events2preds.replace('', np.nan, inplace=True)
    events2preds[numerical_features] = events2preds[numerical_features].astype(float)
    events2preds[numerical_features] = events2preds[numerical_features].fillna(events2preds[numerical_features].mean())
    for col in categorical_features:
        events2preds[col] = events2preds[col].astype(str)

    preds = model.predict_proba(events2preds[features])
    ans['preds'] = preds.tolist()
    ans['Дата создания во внешней системе'] = ans['Дата создания во внешней системе'].dt.strftime('%d.%m.%Y')

    ans = {"predict": ans[['Дата создания во внешней системе', 'preds']].set_index('Дата создания во внешней системе')[
        'preds'].to_dict()}

    events = events[(events['Дата создания во внешней системе'] >= date_start) &
                    (events['Дата создания во внешней системе'] <= date_end)]
    ans['incidents_count'] = events.groupby('Наименование').count()['Дата создания во внешней системе'].to_dict()

    odpu_stat = odpu[['Месяц/Год', 'volume1forhour', 'volume2forhour', 'q2forhour', 'difference_supply_return_mix_all',
                      'difference_supply_return_leak_all', 'temperature_supply_all', 'temperature_return_all']]
    odpu_stat = odpu_stat[(odpu_stat['Месяц/Год'] >= date_start) &
                          (odpu_stat['Месяц/Год'] <= date_end)]
    odpu_stat['Месяц/Год'] = odpu_stat['Месяц/Год'].dt.strftime('%d.%m.%Y')
    odpu_stat[['volume1forhour', 'volume2forhour', 'q2forhour']] *= 24
    odpu_stat.rename(columns={
        'volume1forhour': 'volume1', 'volume2forhour': 'volume2', 'q2forhour': 'q2'
    }, inplace=True)
    odpu_stat[['volume1', 'volume2', 'q2']] = odpu_stat[['volume1', 'volume2', 'q2']].fillna(
        odpu_stat[['volume1', 'volume2', 'q2']].mean())

    ans['odpu_plot'] = odpu_stat.set_index('Месяц/Год').to_dict()

    return ans


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


def get_stats_from_bd(date, conn):
    """
    Вспомогательная функция для получения статистических данных из базы данных.

    Аргументы:
        date (datetime.datetime): Дата, для которой необходимо получить статистические данные.
        conn (connection): Соединение с базой данных.

    Возвращает:
        dict: Структурированные статистические данные на основе указанной даты.

    Описание:
        - Извлекает события из базы данных, которые произошли в пределах последних двух недель до указанной даты.
        - Переименовывает столбцы для соответствия заданной схеме и фильтрует события по ключевым наименованиям.
        - Подсчитывает количество событий по категориям, количество завершённых и текущих задач.
        - Извлекает погодные данные из файла 'weather.json' на основе указанной даты.
        - Вычисляет количество уникальных УНОМов и количество объектов без событий в базе данных.
    """
    ans = {}

    events = pd.read_sql(
        f"""
        SELECT *
        FROM events
        WHERE 
            events.creation_date <= '{date.strftime("%Y-%m-%d")}'
            AND events.creation_date >= '{(date - pd.Timedelta(days=14)).strftime("%Y-%m-%d")}'
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

    events['Наименование'] = events['Наименование'].apply(lambda x: eventNames2labels[x])
    events['Дата создания во внешней системе'] = pd.to_datetime(events['Дата создания во внешней системе'])
    events['Дата и время завершения события'] = pd.to_datetime(events['Дата и время завершения события'])
    # events.sort_values(by='Дата создания во внешней системе', inplace=True, ignore_index=True)

    counts = events.groupby('Наименование').count()['Дата создания во внешней системе']

    ans['event_counts'] = counts.to_dict()
    ans['count_collect_tasks'] = len(events[events['Дата и время завершения события'] <= date])
    ans['count_current_tasks'] = len(events[events['Дата создания во внешней системе'] <= date])

    with open('./configs/weather.json', 'r', encoding='utf-8') as file:
        weather = json.load(file)

    mon = num2month[date.month]
    day = "{:02d}".format(date.day)
    weather1, weather2 = weather[mon][day]
    ans['weather1'] = weather1
    ans['weather2'] = weather2

    n_unique_unoms = \
        pd.read_sql("SELECT COUNT(DISTINCT unom) AS unique_unom_count FROM buildings;", conn).unique_unom_count[0]
    n_unique_unoms_with_event = events['УНОМ'].nunique()
    ans['n_unoms_without_events'] = int(n_unique_unoms) - int(n_unique_unoms_with_event)

    return ans


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
    """
    Добавляет агрегированные признаки из данных ОДПУ (Объединенные данные по потреблению) к строке данных.

    Аргументы:
        odpu (DataFrame): DataFrame с данными ОДПУ, содержащими информацию о потреблении для различных объектов.
        row (Series): Строка данных, к которой добавляются признаки.

    Возвращает:
        Series: Обновленная строка данных с добавленными агрегированными признаками из ОДПУ.

    Описание:
        - Фильтрует данные ОДПУ для конкретного объекта (УНОМ) и оставляет только те записи, которые предшествуют текущему времени (curr_time).
        - Ограничивает выборку последних записей до 14 (если записей больше 14).
        - Рассчитывает и добавляет к строке средние значения, стандартное отклонение, минимальные, максимальные и медианные значения для указанных признаков.
        - Добавляет последние доступные значения признаков 'Потребители', 'Группа', 'Центральное отопление(контур)', 'Ошибки' или None, если данных нет.
    """
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
    """
    Возвращает таблицу ОДПУ, обрезанную по дате.

    Аргументы:
        date (datetime.datetime): Дата, по которой будет обрезана таблица ОДПУ.
        conn: Соединение с базой данных PostgreSQL.

    Возвращает:
        pd.DataFrame: DataFrame с данными ОДПУ, содержащий информацию о потреблении тепловой энергии за последние 14 дней до указанной даты.

    Описание:
        - Загружает данные из таблицы heating_data из базы данных PostgreSQL, обрезанные по дате, с использованием SQL-запроса.
        - Переименовывает столбцы для удобства использования.
        - Преобразует столбец 'Месяц/Год' в формат datetime.
        - Фильтрует данные, оставляя только записи за последние 14 дней до указанной даты.
        - Сортирует данные по столбцу 'Месяц/Год'.
        - Преобразует столбец 'Объём поданого теплоносителя в систему ЦО' в формат float.
        - Добавляет новые признаки 'volume1forhour', 'volume2forhour', 'q2forhour', которые вычисляются на основе объема теплоносителя и наработки часов счётчика.

    """
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
    """
    Возвращает данные ОДПУ для одного объекта за последние 14 дней до указанной даты.

    Аргументы:
        unom (int): Уникальный номер объекта (УНОМ).
        date (datetime.datetime): Дата, по которой будет обрезана таблица ОДПУ.
        conn: Соединение с базой данных PostgreSQL.

    Возвращает:
        pd.DataFrame: DataFrame с данными ОДПУ для указанного объекта (УНОМ), содержащий информацию о потреблении тепловой энергии за последние 14 дней до указанной даты.

    Описание:
        - Загружает данные из таблицы heating_data из базы данных PostgreSQL, отфильтрованные по уникальному номеру объекта (УНОМ) и обрезанные по дате, с использованием SQL-запроса.
        - Переименовывает столбцы для удобства использования.
        - Преобразует столбец 'Месяц/Год' в формат datetime.
        - Фильтрует данные, оставляя только записи за последние 14 дней до указанной даты.
        - Сортирует данные по столбцу 'Месяц/Год'.
        - Преобразует столбец 'Объём поданого теплоносителя в систему ЦО' в формат float.
        - Добавляет новые признаки 'volume1forhour', 'volume2forhour', 'q2forhour', которые вычисляются на основе объема теплоносителя и наработки часов счётчика.

    """
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
    odpu['difference_supply_return_mix_all'] = odpu['Разница между подачей и обраткой(Подмес)'].astype(float) / (
        odpu['Наработка часов счётчика']) * 24
    odpu['difference_supply_return_leak_all'] = odpu['Разница между подачей и обраткой(Утечка)'].astype(float) / (
        odpu['Наработка часов счётчика']) * 24
    odpu['temperature_supply_all'] = odpu['Температура подачи'].astype(float) / (odpu['Наработка часов счётчика']) * 24
    odpu['temperature_return_all'] = odpu['Температура обратки'].astype(float) / (odpu['Наработка часов счётчика']) * 24

    return odpu


def get_agg_data(conn) -> pd.DataFrame:
    """
    Возвращает агрегированные данные из таблицы buildings.

    Аргументы:
        conn: Соединение с базой данных PostgreSQL.

    Возвращает:
        pd.DataFrame: DataFrame с агрегированными данными из таблицы buildings.

    Описание:
        - Выполняет SQL-запрос для получения всех данных из таблицы buildings.
        - Преобразует результат запроса в DataFrame.
        - Переименовывает столбцы для удобства использования.
    """
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
    """
    Возвращает агрегированные данные из таблицы buildings для конкретного UNOM.

    Аргументы:
        unom: Уникальный идентификатор объекта недвижимости.
        conn: Соединение с базой данных PostgreSQL.

    Возвращает:
        pd.DataFrame: DataFrame с агрегированными данными из таблицы buildings для указанного UNOM.

    Описание:
        - Выполняет SQL-запрос для получения данных из таблицы buildings для конкретного UNOM.
        - Преобразует результат запроса в DataFrame.
        - Переименовывает столбцы для удобства использования.
    """
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
    """
    Агрегирует события из таблицы events для указанной строки датасета.

    Аргументы:
        row: Строка датасета, для которой собираются события.
        events: DataFrame с данными событий.

    Возвращает:
        pd.Series: Строка с добавленными признаками событий для указанной строки.

    Описание:
        - Фильтрует события по УНОМ и времени создания внешней системы.
        - Группирует события по наименованию и месяцу создания и считает количество событий.
        - Добавляет количество событий разных типов и за разные месяцы в исходную строку датасета.

    Пример:
        >>> row = {'УНОМ': 123456789, 'Дата создания во внешней системе': datetime.datetime(2024, 6, 17)}
        >>> events_df = pd.DataFrame(...)
        >>> updated_row = collect_events(row, events_df)
        >>> print(updated_row)
    """
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
    """
    Добавляет информацию о погоде в указанную строку набора данных.

    Аргументы:
        row (pd.Series): Строка набора данных, к которой будет добавлена информация о погоде.
        weather (dict): Словарь, содержащий данные о погоде, полученные из внешнего сервиса.

    Возвращает:
        pd.Series: Строка с добавленными признаками погоды 'weather1' и 'weather2'.

    Описание:
        - Извлекает данные о погоде для указанной даты из словаря 'weather'.
        - Обновляет строку признаками 'weather1' и 'weather2' на основе извлеченных данных.
    """
    mon = num2month[row.month]
    day = "{:02d}".format(row.day)
    try:
        row['weather1'], row['weather2'] = weather[mon][day]
    except:
        row['weather1'], row['weather2'] = '', ''
    return row[['weather1', 'weather2']]


def get_events(date, conn) -> pd.DataFrame:
    """
    Получает события из базы данных, которые произошли до указанной даты.

    Аргументы:
        date (datetime.datetime): Дата, до которой нужно получить события.
        conn (connection): Соединение с базой данных.

    Возвращает:
        pd.DataFrame: Набор данных о событиях, включающий информацию о наименовании,
                     источнике, дате создания во внешней системе, УНОМ, месяце и дне.

    Описание:
        - Извлекает события из базы данных, которые произошли до указанной даты.
        - Переименовывает столбцы для соответствия заданной схеме.
        - Фильтрует события по заданным наименованиям и переименовывает их соответственно.
        - Преобразует столбец 'Дата создания во внешней системе' в формат datetime.
        - Сортирует события по дате создания во внешней системе.
    """
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
    """
    Получает события из базы данных для конкретного УНОМа до указанной даты.

    Аргументы:
        unom (int): УНОМ (уникальный номер объекта теплоснабжения), для которого нужно получить события.
        date (datetime.datetime): Дата, до которой нужно получить события.
        conn (connection): Соединение с базой данных.

    Возвращает:
        pd.DataFrame: Набор данных о событиях для указанного УНОМа, включающий информацию
                     о наименовании, источнике, дате создания во внешней системе, месяце и дне.

    Описание:
        - Извлекает события из базы данных, которые произошли до указанной даты для заданного УНОМа.
        - Переименовывает столбцы для соответствия заданной схеме.
        - Фильтрует события по заданным наименованиям и переименовывает их соответственно.
        - Преобразует столбец 'Дата создания во внешней системе' в формат datetime.
        - Сортирует события по дате создания во внешней системе.
    """
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
    """Извлекает временные признаки из столбца с датами.

    Аргументы:
        df (pd.DataFrame): DataFrame, содержащий данные.
        date_col (str): Название столбца с датами.

    Возвращает:
        pd.DataFrame: Обновленный DataFrame с добавленными временными признаками.
    """
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
    """Добавляет циклические признаки в DataFrame.

    Аргументы:
        df (pd.DataFrame): DataFrame, содержащий данные.
        col (str): Название столбца, для которого добавляются циклические признаки.
        max_val (int): Максимальное значение для нормализации циклического признака.

    Возвращает:
        pd.DataFrame: Обновленный DataFrame с добавленными циклическими признаками.
    """
    df[col + '_sin'] = np.sin(2 * np.pi * df[col] / max_val)
    df[col + '_cos'] = np.cos(2 * np.pi * df[col] / max_val)
    return df


class CatBoostModel:
    def __init__(self, data, type_description_dict, material_parameters_dict,
                 model_path='./configs/catboost_for_house_cooling.cbm'):
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
            print(f"Ошибка при подключении к базе данных: {e}")
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

        data_for_catboost['hours_until_cooling'] = data_for_catboost.apply(lambda row: time_count(row), axis=1)
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

                apartment_tags = ['многоквартирный дом', 'блокированный жилой дом', 'общежитие', 'спальный корпус',
                                  'гараж', 'дом ребенка', 'интернат', 'гостиница']
                social_tags = ['школа', 'библиотека', 'музей', 'детский сад', 'колледж', 'больница', 'родильный дом',
                               'поликлиника', 'ясли-сад', 'медучилище', 'дом детского творчества', 'музыкальная школа',
                               'школа-интернат', 'гимназия', 'лечебный корпус', 'санаторий', 'центр реабилитации',
                               'спецшкола', 'училище', 'лечебное', 'учебное', 'учебно-производственный комбинат',
                               'культурно-просветительное', 'техническое училище', 'техникум', 'школа-сад',
                               'детские ясли', 'станция скорой помощи', 'спортивная школа', 'наркологический диспансер',
                               'профтехучилище', 'спортивный клуб', 'лаборатория', 'детский санаторий', 'диспансер',
                               'дворец пионеров', 'детсад-ясли', 'детский дом культуры', 'ясли',
                               'физкультурно-оздоровительный комплекс', 'клуб', 'бассейн и спортзал',
                               'спортивный корпус', 'детское дошкольное учреждение', 'подстанция скорой помощи',
                               'блок-пристройка начальных классов', 'спортивное', 'кафе', 'столовая',
                               'центр обслуживания']
                industrial_tags = ['трансформаторная подстанция', 'нежилое', 'выставочный павильон',
                                   'кухня клиническая', 'хозблок', 'овощехранилище', 'учреждение',
                                   'хирургический корпус', 'морг', 'пищеблок', 'учебно-воспитателный комбинат',
                                   'учреждение,мастерские', 'дезинфекционная камера',
                                   'отделение судебно-медицинской экспертизы', 'пункт охраны', 'учебный корпус',
                                   'плавательный бассейн', 'хранилище', 'административное', 'научное', 'архив',
                                   'учебно-воспитательное', 'терапевтический корпус', 'учебное',
                                   'административно-бытовой']

                energy_efficiency = new_dict['Класс энергоэффективности здания']
                energy_efficiency_mapping = {'A++': 2, 'A+': 3, 'A': 4, 'B': 5, 'C': 6, 'D': 7, 'E': 8, 'F': 9,
                                             'G': 10}  # Словарь для сопоставления уровня энергоэффективности с числовым значением
                efficiency_weight = energy_efficiency_mapping.get(energy_efficiency,
                                                                  1)  # По умолчанию, если энергоэффективность неизвестна или некорректна

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
                working_time_mapping = {'Круглосуточно': 3, '9:00 - 21:00': 2,
                                        '9:00 – 18:00': 1}  # Словарь для сопоставления графика работы с числовым значением
                working_weight = working_time_mapping.get(working_time,
                                                          1)  # По умолчанию, если график работы неизвестен или некорректен

                if hours <= 2:
                    # приоритет максимальный (1)
                    return 1
                else:
                    # Формула для расчета приоритета
                    return (hours / (weight + efficiency_weight + working_weight))
            else:
                return None

        except Exception as e:
            print(f"Ошибка при подключении к базе данных: {e}")
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


def get_current_inside_temperature():
    """
    Функция для получения прогноза погоды от Яндекс.Погоды по координатам.
    :param lat: Широта
    :param lon: Долгота
    :return: Прогноз погоды
    """
    # url = f'https://api.weather.yandex.ru/v2/forecast?lat=55.787715&lon=37.775631'
    # headers = {'X-Yandex-Weather-Key': "0281e1b2-1d86-4735-a2b6-6a77b605fb86"}

    # response = requests.get(url, headers=headers)

    # if response.status_code == 200:
    #     return response.json()["fact"]["temp"]
    # else:
    #     print(f"Ошибка при запросе: {response.status_code}")
    #     return None
    return 22


def get_weather_forecast():
    """
    Функция для получения прогноза погоды от Яндекс.Погоды по координатам.
    :param lat: Широта
    :param lon: Долгота
    :return: Прогноз погоды
    """

    # Получаем текущую дату и время
    # now = int(get_current_inside_temperature())

    # url = f'https://api.weather.yandex.ru/v2/forecast?lat=55.787715&lon=37.775631'
    # headers = {'X-Yandex-Weather-Key': "0281e1b2-1d86-4735-a2b6-6a77b605fb86"}

    # response = requests.get(url, headers=headers)

    # if response.status_code == 200:
    #     return {
    #         't_in_5_hours': now,
    #         't_in_10_hours': now,
    #         't_in_15_hours': now,
    #         't_in_20_hours': now,
    #         't_in_25_hours': now,
    #         't_in_30_hours': now
    #     }
    # else:
    #     print(f"Ошибка при запросе: {response.status_code}")
    #     return None
    weather = pd.read_csv("./configs/weather_forecast.csv")
    weather_forecast = weather['temperature'].head(6).tolist()
    return {
        't_in_5_hours': weather_forecast[0],
        't_in_10_hours': weather_forecast[1],
        't_in_15_hours': weather_forecast[2],
        't_in_20_hours': weather_forecast[3],
        't_in_25_hours': weather_forecast[4],
        't_in_30_hours': weather_forecast[5]
    }


def connect_to_db():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        print("1Ошибка при подключении к базе данных: {e}")
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

        t_inside = [get_current_inside_temperature()] * len(unoms)
        t_outside = get_weather_forecast()

        # Получаем предсказания
        catboost_model = CatBoostModel(database, type_description_dict, material_parameters_dict,
                                       model_path='./models/catboost_for_house_cooling.cbm')
        data_for_catboost = catboost_model.prepare_data_for_catboost(unoms, t_inside, t_outside)
        catboost_predictions = catboost_model.get_catboost_predictions(data_for_catboost)
        df_sorted = catboost_model.get_final_ranking(catboost_predictions)

        return df_sorted.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


def time_count(row):
    conn = connect_to_db()
    specific_date = datetime.datetime(2024, 1, 1)

    stat_data = get_stats_from_bd(specific_date, conn)
    T1 = float(stat_data["weather1"])  # температура снаружи дома

    ro = 1.225  # плотность воздуха
    c = 1005  # теплоемкость воздуха
    T0 = 22  # температура внутри дома
    V = float(row["V"])
    alpha = float(row["alpha"])
    A = float(row["A"])
    T2 = 18  # температура в доме через time часов

    if T1 > 18:
        time = 999999
    else:
        time = ((math.log((T0 - T1) / (T2 - T1)) * c * ro * V) / (alpha * A)) / 3600
        time *= 1000
    return int(time)


type_description_file_path = "./configs/type_descriptions.json"
material_parameters_file_path = "./configs/material_parameters.json"

with open(type_description_file_path, 'r', encoding='utf-8') as file:
    type_description_dict = json.load(file)

with open(material_parameters_file_path, 'r', encoding='utf-8') as file:
    material_parameters_dict = json.load(file)

if __name__ == "__main__":
    uvicorn.runда(app, host="0.0.0.0", port=8000)