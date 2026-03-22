#!/bin/sh
set -e

echo "Creating database '$POSTGRES_DB' if it does not exist..."
PGPASSWORD="$POSTGRES_PASSWORD" psql \
  -h "$POSTGRES_HOST" \
  -p "$POSTGRES_PORT" \
  -U "$POSTGRES_USER" \
  -d postgres \
  -tc "SELECT 1 FROM pg_database WHERE datname = '$POSTGRES_DB'" \
  | grep -q 1 || PGPASSWORD="$POSTGRES_PASSWORD" createdb \
    -h "$POSTGRES_HOST" \
    -p "$POSTGRES_PORT" \
    -U "$POSTGRES_USER" \
    "$POSTGRES_DB"
echo "Database ready."

echo "Running database migrations..."
for f in /app/migrations/*.sql; do
  echo "Applying $f..."
  PGPASSWORD="$POSTGRES_PASSWORD" psql \
    -h "$POSTGRES_HOST" \
    -p "$POSTGRES_PORT" \
    -U "$POSTGRES_USER" \
    -d "$POSTGRES_DB" \
    -f "$f"
done
echo "Migrations complete."

exec "$@"
