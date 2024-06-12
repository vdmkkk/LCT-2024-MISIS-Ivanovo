-- +goose Up
-- +goose StatementBegin
CREATE TABLE IF NOT EXISTS events (
                        name TEXT,
                        source TEXT,
                        creation_date TEXT,
                        closure_date TEXT,
                        district TEXT,
                        unom INTEGER,
                        address TEXT,
                        event_completion_date TEXT
);
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DROP TABLE IF EXISTS events;
-- +goose StatementEnd
