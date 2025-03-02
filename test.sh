#!/bin/bash

set -e  # Exit script if any command fails

echo "🛑 Stopping any existing test containers..."
docker-compose -f docker-compose-test.yml down -v  # Stop test containers

echo "🚀 Starting test containers..."
docker-compose -f docker-compose-test.yml up -d --build  # Start test containers

# Wait for PostgreSQL
echo "⏳ Waiting for test database to be ready..."
until docker exec test_db pg_isready -U test_admin -d test_odds_db; do
  sleep 2
done
echo "✅ Test database is ready!"

# Wait for Redis
echo "⏳ Waiting for test Redis..."
until nc -z localhost 6380; do
  sleep 2
done
echo "✅ Test Redis is ready!"

# Wait for Scraper API
echo "⏳ Waiting for test Scraper API..."
until curl -s http://localhost:8002/docs > /dev/null; do
  sleep 2
done
echo "✅ Test Scraper API is ready!"

# echo "🧪 Running tests..."
# docker exec test_scraper pytest --disable-warnings || exit 1

# Stop test containers after tests
echo "🛑 Stopping test containers..."
# docker-compose -f docker-compose-test.yml down -v --remove-orphans
