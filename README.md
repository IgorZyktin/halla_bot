# Halla LLM Bot

Маленький бот для проксирования запросов из локальной `LLM` в `Telegram`.

## Запуск бота на сервере

Файл с переменными:

> /etc/halla_bot/env

Содержимое:

```shell
HALLA_BOT__VENV=/home/halla_bot/halla_bot/.venv/bin/python3
HALLA_BOT__TOKEN=<токен для бота>
HALLA_BOT__API_URL=<url до машины, на которой фактически исполняется нейросеть>
HALLA_BOT__DB_PATH=/home/halla_bot/halla_bot.db
HALLA_BOT__LOG_PATH=/var/log/halla_bot.log
```

[Файл для `systemd`](./etc/halla_bot.service).

Активация сервиса:

```shell
sudo cp /home/halla_bot/halla_bot/etc/halla_bot.service /etc/systemd/system/halla_bot.service
sudo systemctl start halla_bot
sudo systemctl enable halla_bot
sudo systemctl status halla_bot
```
