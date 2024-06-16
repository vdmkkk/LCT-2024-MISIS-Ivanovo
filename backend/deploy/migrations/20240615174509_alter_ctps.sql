-- +goose Up
-- +goose StatementBegin
ALTER TABLE ctps
    DROP COLUMN polygon;
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
ALTER TABLE ctps
    ADD COLUMN polygon DOUBLE PRECISION[];
-- +goose StatementEnd
