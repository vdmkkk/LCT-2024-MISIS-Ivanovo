-- +goose Up
-- +goose StatementBegin
ALTER TABLE buildings
    ADD COLUMN energy_efficiency_class VARCHAR,
    ADD COLUMN phone_number_new VARCHAR,
    ADD COLUMN work_hours VARCHAR;
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
ALTER TABLE buildings
    DROP COLUMN energy_efficiency_class,
    DROP COLUMN phone_number_new,
    DROP COLUMN work_hours;
-- +goose StatementEnd
