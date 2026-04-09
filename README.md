# 🏓 PingTest Bot — Discord.js

Discord-бот для мониторинга пинга, состояния сервера и аптайма.

## 🚀 Возможности

- **`/ping`** — WebSocket, API пинг и отклик команды
- **`/system`** — загрузка CPU, RAM, диск
- **`/pingtest`** — пинг до популярных сайтов (google.com, discord.com, github.com, yandex.ru, cloudflare.com)
- **`/uptime`** — время непрерывной работы бота

## 📦 Установка

```bash
npm install
```

## ⚙️ Настройка

1. Скопируйте `.env.example` в `.env`:
   ```bash
   cp .env.example .env
   ```

2. Вставьте токен вашего бота в `.env`:
   ```env
   DISCORD_TOKEN=ваш_токен_здесь
   ```

   Получить токен → [Discord Developer Portal](https://discord.com/developers/applications)

## ▶️ Запуск

```bash
npm start
```

Режим разработки (автоматический перезапуск):

```bash
npm run dev
```

## 📁 Структура проекта

```
PingTestJS/
├── .env            # Токен бота (не коммитится)
├── .env.example    # Шаблон env-файла
├── .gitignore
├── package.json
├── bot.js          # Основной код бота
└── README.md
```

## 🛠 Зависимости

| Пакет | Назначение |
|---|---|
| [discord.js](https://discord.js.org/) | Общение с Discord API |
| [dotenv](https://www.npmjs.com/package/dotenv) | Загрузка переменных окружения |
| [systeminformation](https://www.npmjs.com/package/systeminformation) | CPU, RAM, диск |
| [ping](https://www.npmjs.com/package/ping) | ICMP пинг до хостов |
