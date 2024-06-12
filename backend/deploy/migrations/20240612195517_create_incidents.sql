-- +goose Up
-- +goose StatementBegin
CREATE TABLE IF NOT EXISTS incidents (
    id SERIAL PRIMARY KEY,
    coordinates DOUBLE PRECISION[],
    ctp_id VARCHAR,
    payload JSONB
);

CREATE TABLE IF NOT EXISTS handled_unoms (
    id SERIAL PRIMARY KEY,
    unom INTEGER,
    hours_to_cool INTEGER,
    priority_group INTEGER
);

CREATE TABLE IF NOT EXISTS incidents_handled_unoms (
    incident_id INTEGER REFERENCES incidents(id),
    handled_unom INTEGER REFERENCES handled_unoms(id)
);
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DROP TABLE IF EXISTS incidents, handled_unoms, incidents_handled_unoms;
-- +goose StatementEnd
