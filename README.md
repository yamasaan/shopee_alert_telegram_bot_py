# shopee_alert_telegram_bot_py

Shopee alert product in stock

### Dockerfile

```sh
ENV BOT_TOKEN=xxx
```

### Docker Build

```sh
docker build -t shopee_alert_telegram_bot_py .
```

### Docker run on container

```sh
docker run shopee_alert_telegram_bot_py:latest
```

### Save tar.gz

```sh
docker save shopee_alert_telegram_bot_py:latest | gzip > shopee_alert_telegram_bot_py_latest.tar.gz
```
