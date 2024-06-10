-- +goose Up
-- +goose StatementBegin
ALTER TABLE buildings
    DROP COLUMN municipal_district_1;
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
ALTER TABLE buildings
    ADD COLUMN municipal_district_1 TEXT;
-- +goose StatementEnd
