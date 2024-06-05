-- +goose Up
-- +goose StatementBegin
CREATE TABLE IF NOT EXISTS geolocations (
  id SERIAL PRIMARY KEY,
  data JSONB
);
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DROP TABLE IF EXISTS geolocations;
-- +goose StatementEnd
