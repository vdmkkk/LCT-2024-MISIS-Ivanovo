-- +goose Up
-- +goose StatementBegin
CREATE TABLE IF NOT EXISTS tecs (
    name VARCHAR,
    address VARCHAR,
    phone_number VARCHAR,
    coordinates DOUBLE PRECISION[]
);
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DROP TABLE IF EXISTS tecs;
-- +goose StatementEnd
