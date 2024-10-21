-- Create enum for status messages
CREATE TYPE status_message AS ENUM ('valid_position', 'last_known_position', 'invalid_position');

-- Create devices table
CREATE TABLE devices (
    device_id VARCHAR(50) PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create locations table
CREATE TABLE locations (
    location_id SERIAL PRIMARY KEY,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL
);

-- Create asset_data table
CREATE TABLE asset_data (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(50) NOT NULL,
    voltage DECIMAL(5, 2) NOT NULL,
    status status_message NOT NULL,
    location_id INTEGER,
    current_speed DECIMAL(5, 2),
    gps_date DATE NOT NULL,
    gps_time TIME NOT NULL,
    inserted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(device_id),
    FOREIGN KEY (location_id) REFERENCES locations(location_id)
);

-- Create index on device_id and inserted_at for faster queries
CREATE INDEX idx_asset_data_device_id_inserted_at ON asset_data(device_id, inserted_at);

-- Create index on location_id for faster joins
CREATE INDEX idx_asset_data_location_id ON asset_data(location_id);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(65) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
