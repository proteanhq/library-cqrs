#!/bin/bash

# Variables for database connection
DB_HOST="localhost"
DB_PORT="5432"
DB_ADMIN="postgres"  # The database admin user (e.g., 'postgres')
DB_ADMIN_PASSWORD="postgres"

# Variables for the new user and database
DB_NAME="test_postgres"
DB_USER="test_postgres"
DB_USER_PASSWORD="test_postgres"

# SQL commands to create the user and database
SQL_CREATE_DB=$(cat <<EOF
CREATE USER $DB_USER WITH PASSWORD '$DB_USER_PASSWORD';
CREATE DATABASE $DB_NAME;
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
EOF
)

# SQL commands to grant schema-level privileges
SQL_GRANT_PRIVILEGES=$(cat <<EOF
GRANT ALL PRIVILEGES ON SCHEMA public TO $DB_USER;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $DB_USER;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $DB_USER;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO $DB_USER;
EOF
)

# Execute the SQL commands to create the user and database
PGPASSWORD="$DB_ADMIN_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_ADMIN" -d postgres -c "$SQL_CREATE_DB"

# Execute the SQL commands to grant schema-level privileges by connecting to the newly created database
PGPASSWORD="$DB_ADMIN_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_ADMIN" -d "$DB_NAME" -c "$SQL_GRANT_PRIVILEGES"