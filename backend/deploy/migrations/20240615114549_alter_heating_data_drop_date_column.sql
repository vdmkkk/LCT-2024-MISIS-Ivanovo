-- +goose Up
-- +goose StatementBegin
ALTER TABLE heating_data
    DROP COLUMN date;
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
ALTER TABLE heating_data
    ADD COLUMN date DATE;
-- +goose StatementEnd
