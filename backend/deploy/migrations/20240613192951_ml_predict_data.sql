-- +goose Up
-- +goose StatementBegin
CREATE TABLE IF NOT EXISTS ml_predict (
    unom BIGINT,
    datetime VARCHAR,
    probabilites DOUBLE PRECISION[]
);
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DROP TABLE IF EXISTS ml_predict;
-- +goose StatementEnd
