docker network create shared_env_net

docker compose up init-airflow --build

sleep 5

docker compose up -d --build

sleep 5

cd airbyte

# Check if docker-compose.yml exists in the current directory
if [ -f "docker-compose.yaml" ]; then
  # If it exists, run docker-compose up
  docker-compose up -d
else
  # Otherwise, run the setup script
  ./run-ab-platform.sh
fi