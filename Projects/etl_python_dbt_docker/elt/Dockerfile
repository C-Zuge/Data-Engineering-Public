FROM python:3.8-slim

RUN apt-get update && apt-get install -y postgresql-client-15 cron

COPY start.sh /app/start.sh
COPY elt.py .

WORKDIR /app

RUN echo "0 3 * * * python /app/elt.py" | crontab -

# Set the default command to run the ELT script
CMD ["python", "elt.py"]