-- +goose Up
-- +goose StatementBegin
ALTER TABLE heating_data
    ALTER COLUMN unom TYPE BIGINT,
    ALTER COLUMN id_uu TYPE BIGINT,
    ALTER COLUMN id_tu TYPE BIGINT;
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
ALTER TABLE heating_data
    ALTER COLUMN unom TYPE INTEGER,
    ALTER COLUMN id_uu TYPE INTEGER,
    ALTER COLUMN id_tu TYPE INTEGER;
-- +goose StatementEnd
