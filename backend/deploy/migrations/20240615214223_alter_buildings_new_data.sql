-- +goose Up
-- +goose StatementBegin
ALTER TABLE buildings
    DROP COLUMN external_system_id;
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
ALTER TABLE buildings
    ADD COLUMN external_system_id double precision;
-- +goose StatementEnd
