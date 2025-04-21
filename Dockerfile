FROM debian:12
RUN apt -y update && apt upgrade -y && apt install -y python3 python3-pip chromium chromium-driver cron
WORKDIR /app/
RUN pip install undetected-chromedriver selenium SQLAlchemy --break-system-packages
COPY app.py entrypoint.sh /app/
COPY crontab /etc
RUN chmod 0644 /etc/crontab && crontab /etc/crontab
ENTRYPOINT ["bash", "/app/entrypoint.sh"]