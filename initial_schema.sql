-- Create UserBalance table
CREATE TABLE userbalance (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE,
    amount DECIMAL(10,2) NOT NULL DEFAULT 0,
    reserved_amount DECIMAL(10,2) NOT NULL DEFAULT 0,
    CONSTRAINT userbalance_user_id_fk FOREIGN KEY (user_id) REFERENCES auth_user (id)
);

-- Create Transaction table
CREATE TABLE transaction (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT transaction_user_id_fk FOREIGN KEY (user_id) REFERENCES auth_user (id)
);

-- Create FinancialReport table
CREATE TABLE financialreport (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    service_id INTEGER NOT NULL,
    order_id INTEGER NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    recognized_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT financialreport_user_id_fk FOREIGN KEY (user_id) REFERENCES auth_user (id)
);