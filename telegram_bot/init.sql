CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    name VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(100),
    user_type VARCHAR(20) CHECK (user_type IN ('Company', 'Individual')),
    deal_id BIGINT
);
