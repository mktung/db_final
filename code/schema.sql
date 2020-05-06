DROP SCHEMA IF EXISTS stocks_and_attacks CASCADE;
CREATE SCHEMA stocks_and_attacks;
DROP TABLE IF EXISTS historical_stock_prices CASCADE;
DROP TABLE IF EXISTS company_information CASCADE;
DROP TABLE IF EXISTS attacks CASCADE;
DROP TABLE IF EXISTS attack_location CASCADE;
DROP TABLE IF EXISTS attack_data CASCADE;
CREATE EXTENSION IF NOT EXISTS tablefunc;

CREATE TABLE company_information(
    ticker VARCHAR(15),
    exchange VARCHAR(31),
    name VARCHAR(127),
    sector VARCHAR(127),
    industry VARCHAR(127),
    PRIMARY KEY(ticker)
);

CREATE TABLE historical_stock_prices(
    ticker VARCHAR(15) REFERENCES company_information(ticker),
    open NUMERIC(31, 2),
    close NUMERIC(31, 2),
    adj_close NUMERIC(31, 2),
    low NUMERIC(31, 2),
    high NUMERIC(31, 2),
    volume BIGINT,
    trade_date DATE,
    PRIMARY KEY(ticker, trade_date)
);

CREATE TABLE attacks (
	attackID BIGINT PRIMARY KEY,
	date DATE,
	summary VARCHAR(511)
);

CREATE TABLE attack_location (
	attackID BIGINT PRIMARY KEY REFERENCES attacks(attackID),
	country VARCHAR(255),
	region VARCHAR(255),
	provstate VARCHAR(255),
	city VARCHAR(255)
);

CREATE TABLE attack_data (
	attackID BIGINT PRIMARY KEY REFERENCES attacks(attackID),
	extended BOOLEAN,
	multiple BOOLEAN,
	success BOOLEAN,
	suicide BOOLEAN,
    attack_type VARCHAR(255),
    target_type VARCHAR(255),
    target_nationality VARCHAR(255),
    number_killed INTEGER
);
