-- +goose Up
-- +goose StatementBegin
CREATE TABLE IF NOT EXISTS geolocations (
  id SERIAL PRIMARY KEY,
  unom INTEGER UNIQUE,
  coordinates DOUBLE PRECISION[][][]
);
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DROP TABLE IF EXISTS geolocations;
-- +goose StatementEnd
