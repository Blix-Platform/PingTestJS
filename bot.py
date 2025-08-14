import discord
from discord.ext import commands
import os
import time
import psutil
from ping3 import ping
from datetime import datetime, timezone
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Проверка токена
if not TOKEN:
    print("❌ Ошибка: DISCORD_TOKEN не найден в .env файле!")
    exit()

# Настройка интентов и бота
intents = discord.Intents.default()
intents.message_content = True  # обязательно для чтения сообщений

# Используем commands.Bot вместо discord.Bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Время запуска
start_time = datetime.now(timezone.utc)

# Список сайтов для теста пинга
TEST_SITES = [
    "google.com",
    "discord.com",
    "github.com",
    "yandex.ru",
    "cloudflare.com"
]


# === on_ready — когда бот запускается
@bot.event
async def on_ready():
    print(f"✅ {bot.user} успешно запущен!")
    await bot.change_presence(activity=discord.Game(name="!ping | Тест пинга"))


# === Команда: !ping
@bot.slash_command(name="ping", description="🏓 Проверить пинг и состояние бота")
async def ping(ctx):
    await ctx.defer(ephemeral=False)

    # WebSocket пинг
    ws_ping = bot.latency * 1000

    # Command пинг (замеряем время ответа)
    start = time.time()
    await ctx.respond("⏳", delete_after=0.1)
    cmd_ping = (time.time() - start) * 1000

    # API пинг
    api_start = time.time()
    try:
        await bot.fetch_user(bot.user.id)
        api_ping = (time.time() - api_start) * 1000
    except:
        api_ping = None

    # Оценка пинга
    if ws_ping < 100:
        status = "🟢 Отлично"
    elif ws_ping < 200:
        status = "🟡 Удовлетворительно"
    else:
        status = "🔴 Высокий"

    # Аптайм
    uptime = datetime.now(timezone.utc) - start_time
    hours, rem = divmod(int(uptime.total_seconds()), 3600)
    mins, sec = divmod(rem, 60)
    days, hours = divmod(hours, 24)
    uptime_str = f"{days}д {hours}ч" if days else f"{hours}ч {mins}м"

    # Embed
    embed = discord.Embed(
        title="🏓 Состояние бота",
        color=0x5865F2,
        timestamp=datetime.now(timezone.utc)
    )

    embed.add_field(
        name="📡 WebSocket пинг",
        value=f"```{ws_ping:.1f} мс```",
        inline=True
    )
    embed.add_field(
        name="💬 Отклик команды",
        value=f"```{cmd_ping:.1f} мс```",
        inline=True
    )
    embed.add_field(
        name="📤 API пинг",
        value=f"```{api_ping:.1f} мс```" if api_ping else "```⚠️ Ошибка```",
        inline=True
    )

    embed.add_field(
        name="📊 Статус",
        value=status,
        inline=True
    )
    embed.add_field(
        name="⏱️ Аптайм",
        value=f"```{uptime_str}```",
        inline=True
    )
    embed.add_field(
        name="🖥️ Серверов",
        value=f"```{len(bot.guilds):,}```",
        inline=True
    )

    embed.set_thumbnail(url=bot.user.display_avatar.url)
    embed.set_footer(text="PingTest Bot • Диагностика", icon_url=bot.user.display_avatar.url)

    await ctx.respond(embed=embed)


# === Команда: !system
@bot.slash_command(name="system", description="🖥️ Показать состояние сервера")
async def system(ctx):
    await ctx.defer(ephemeral=False)

    cpu_usage = psutil.cpu_percent()
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    ram_used = ram.used / (1024**3)
    ram_total = ram.total / (1024**3)
    disk_used = disk.used / (1024**3)
    disk_total = disk.total / (1024**3)

    embed = discord.Embed(
        title="🖥️ Состояние сервера",
        color=0x5865F2,
        timestamp=datetime.now(timezone.utc)
    )

    embed.add_field(
        name="⚡ CPU",
        value=f"```{cpu_usage}%```",
        inline=False
    )
    embed.add_field(
        name="💾 RAM",
        value=f"```{ram_used:.1f} ГБ / {ram_total:.1f} ГБ ({ram.percent}%)```",
        inline=False
    )
    embed.add_field(
        name="💽 Диск",
        value=f"```{disk_used:.1f} ГБ / {disk_total:.1f} ГБ ({disk.percent}%)```",
        inline=False
    )

    embed.set_footer(text="PingTest Bot • Мониторинг", icon_url=bot.user.display_avatar.url)
    await ctx.respond(embed=embed)


# === Команда: !pingtest
@bot.slash_command(name="pingtest", description="🌐 Проверить пинг до сайтов")
async def pingtest(ctx):
    await ctx.defer(ephemeral=False)

    results = []
    for site in TEST_SITES:
        try:
            delay = ping(site, timeout=2)
            if delay is not None:
                delay_ms = delay * 1000
                emoji = "🟢" if delay_ms < 100 else "🟡" if delay_ms < 300 else "🔴"
                results.append(f"{emoji} `{site:15}` → `{delay_ms:6.1f} мс`")
            else:
                results.append(f"🔴 `{site:15}` → `Таймаут`")
        except:
            results.append(f"❌ `{site:15}` → `Ошибка`")

    embed = discord.Embed(
        title="🌐 Тест пинга до сайтов",
        description="\n".join(results),
        color=0x5865F2,
        timestamp=datetime.now(timezone.utc)
    )
    embed.set_footer(text="PingTest Bot • Сеть", icon_url=bot.user.display_avatar.url)
    await ctx.respond(embed=embed)


# === Команда: !uptime
@bot.slash_command(name="uptime", description="⏱️ Показать аптайм бота")
async def uptime_cmd(ctx):
    uptime = datetime.now(timezone.utc) - start_time
    hours, rem = divmod(int(uptime.total_seconds()), 3600)
    mins, sec = divmod(rem, 60)
    days, hours = divmod(hours, 24)
    uptime_str = f"{days}д {hours}ч" if days else f"{hours}ч {mins}м"

    embed = discord.Embed(
        title="⏱️ Аптайм бота",
        description=f"Бот работает: **{uptime_str}**",
        color=0x5865F2,
        timestamp=datetime.now(timezone.utc)
    )
    embed.set_footer(text="PingTest Bot", icon_url=bot.user.display_avatar.url)
    await ctx.respond(embed=embed)


# Запуск бота
bot.run(TOKEN)
