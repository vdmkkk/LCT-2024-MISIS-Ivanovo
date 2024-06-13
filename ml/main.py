import pandas as pd
import datetime
import json

from catboost import CatBoostClassifier
import numpy as np
import psycopg2

from fastapi import FastAPI, HTTPException
import uvicorn
import warnings

warnings.filterwarnings("ignore")


app = FastAPI()


model = CatBoostClassifier()
model.load_model('model_task1')


@app.post("/predict_all/")
async def predict_all(date: datetime.datetime):
    try:
        conn = psycopg2.connect(
            user="ivanovo",
            password="ivanovo",
            host="92.51.39.188",  # локальный хост
            port="5432",  # стандартный порт PostgreSQL
            database="ivanovo"
        )

        # Получаем предсказания
        preds = get_predict_for_all(model, date, conn)

        return preds
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        conn.close()


@app.post("/predict_one/")
async def predict_one(unom:int, date: datetime.datetime, n:int):
    try:
        conn = psycopg2.connect(
            user="ivanovo",
            password="ivanovo",
            host="92.51.39.188",  # локальный хост
            port="5432",  # стандартный порт PostgreSQL
            database="ivanovo"
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


def get_predict_for_one(model: CatBoostClassifier, unom: int, date: datetime.datetime, n:int, conn) -> dict:
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

    
def get_odpu(date:datetime.datetime, conn) -> pd.DataFrame: # возвращает таблицу odpu, ОБРЕЗАННУЮ ПО ДАТЕ 
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
    for month_num in [1,2,3,4,10,11,12]:
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)