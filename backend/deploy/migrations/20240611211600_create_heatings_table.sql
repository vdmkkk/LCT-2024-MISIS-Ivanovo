-- +goose Up
-- +goose StatementBegin
CREATE TABLE heating_data (
                              unom INTEGER, -- UNOM
                              id_uu INTEGER, -- ID УУ
                              id_tu INTEGER, -- ID ТУ
                              district TEXT, -- Округ
                              area TEXT, -- Район
                              consumers TEXT, -- Потребители
                              group_type TEXT, -- Группа
                              address TEXT, -- Адрес
                              central_heating_contour TEXT, -- Центральное отопление(контур)
                              meter_brand TEXT, -- Марка счетчика
                              meter_serial_number TEXT, -- Серия/Номер счетчика
                              date DATE, -- Дата
                              month_year TEXT, -- Месяц/Год
                              unit TEXT, -- Unit
                              volume_supplied DOUBLE PRECISION, -- Объём поданого теплоносителя в систему ЦО
                              volume_returned DOUBLE PRECISION, -- Объём обратного теплоносителя из системы ЦО
                              difference_supply_return_mix DOUBLE PRECISION, -- Разница между подачей и обраткой(Подмес)
                              difference_supply_return_leak DOUBLE PRECISION, -- Разница между подачей и обраткой(Утечка)
                              temperature_supply DOUBLE PRECISION, -- Температура подачи
                              temperature_return DOUBLE PRECISION, -- Температура обратки
                              meter_operating_hours DOUBLE PRECISION, -- Наработка часов счётчика
                              heat_energy_consumption DOUBLE PRECISION, -- Расход тепловой энергии
                              errors TEXT -- Ошибки
);
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DROP TABLE IF EXISTS heating_data;
-- +goose StatementEnd
