import discord
from discord import app_commands
import os
import time
import psutil
import speedtest
from ping3 import ping
from datetime import datetime, timezone
from dotenv import load_dotenv

# Загружаем .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Настройка бота
intents = discord.Intents.default()
bot = discord.Bot(intents=intents)

# Время запуска
start_time = datetime.now(timezone.utc)

# ID сервера поддержки (если нужно)
SUPPORT_SERVER_ID = 123456789012345678  # Замени на свой

# Список сайтов для теста пинга
TEST_SITES = [
    "google.com",
    "discord.com",
    "github.com",
    "yandex.ru",
    "cloudflare.com"
]

# Цвета для embed
COLOR = 0x5865F2  # Официальный цвет Discord


# === /ping — Основная команда пинга ===
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
        color=COLOR,
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
    embed.set_footer(text="PingTest Bot • Тест производительности", icon_url=bot.user.display_avatar.url)

    await ctx.respond(embed=embed)


# === /system — Состояние VPS ===
@bot.slash_command(name="system", description="🖥️ Показать состояние сервера (CPU, RAM, диск)")
async def system(ctx):
    await ctx.defer(ephemeral=False)

    # CPU
    cpu_usage = psutil.cpu_percent()

    # RAM
    ram = psutil.virtual_memory()
    ram_used = ram.used / (1024**3)
    ram_total = ram.total / (1024**3)
    ram_percent = ram.percent

    # Диск
    disk = psutil.disk_usage('/')
    disk_used = disk.used / (1024**3)
    disk_total = disk.total / (1024**3)
    disk_percent = disk.percent

    # Температура (если доступно)
    try:
        temps = psutil.sensors_temperatures()
        temp = temps.get('coretemp', [{}])[0].get('current', 'N/A') if temps else 'N/A'
    except:
        temp = 'N/A'

    embed = discord.Embed(
        title="🖥️ Состояние сервера",
        color=COLOR,
        timestamp=datetime.now(timezone.utc)
    )

    embed.add_field(
        name="⚡ CPU",
        value=f"```{cpu_usage}% загружено```",
        inline=False
    )
    embed.add_field(
        name="💾 RAM",
        value=f"```{ram_used:.1f} ГБ / {ram_total:.1f} ГБ ({ram_percent}%)```",
        inline=False
    )
    embed.add_field(
        name="💽 Диск",
        value=f"```{disk_used:.1f} ГБ / {disk_total:.1f} ГБ ({disk_percent}%)```",
        inline=False
    )
    embed.add_field(
        name="🌡️ Температура",
        value=f"```{temp}°C```",
        inline=False
    )

    embed.set_footer(text="PingTest Bot • Мониторинг VPS", icon_url=bot.user.display_avatar.url)
    await ctx.respond(embed=embed)


# === /pingtest — Пинг до сайтов ===
@bot.slash_command(name="pingtest", description="🌐 Протестировать пинг до популярных сайтов")
async def pingtest(ctx):
    await ctx.defer(ephemeral=False)

    results = []
    for site in TEST_SITES:
        try:
            delay = ping(site, timeout=2)
            if delay is not None:
                delay_ms = delay * 1000
                if delay_ms < 100:
                    emoji = "🟢"
                elif delay_ms < 300:
                    emoji = "🟡"
                else:
                    emoji = "🔴"
                results.append(f"{emoji} `{site:15}` → `{delay_ms:6.1f} мс`")
            else:
                results.append(f"🔴 `{site:15}` → `Таймаут`")
        except:
            results.append(f"❌ `{site:15}` → `Ошибка`")

    embed = discord.Embed(
        title="🌐 Тест пинга до сайтов",
        description="\n".join(results),
        color=COLOR,
        timestamp=datetime.now(timezone.utc)
    )
    embed.set_footer(text="PingTest Bot • Сеть", icon_url=bot.user.display_avatar.url)
    await ctx.respond(embed=embed)


# === /uptime — Аптайм бота ===
@bot.slash_command(name="uptime", description="⏱️ Показать время работы бота")
async def uptime_cmd(ctx):
    uptime = datetime.now(timezone.utc) - start_time
    hours, rem = divmod(int(uptime.total_seconds()), 3600)
    mins, sec = divmod(rem, 60)
    days, hours = divmod(hours, 24)
    if days:
        uptime_str = f"{days} дней, {hours} часов"
    elif hours:
        uptime_str = f"{hours} часов, {mins} минут"
    else:
        uptime_str = f"{mins} минут"

    embed = discord.Embed(
        title="⏱️ Аптайм бота",
        description=f"Бот работает уже **{uptime_str}**",
        color=COLOR,
        timestamp=datetime.now(timezone.utc)
    )
    embed.set_footer(text="PingTest Bot", icon_url=bot.user.display_avatar.url)
    await ctx.respond(embed=embed)


# === Онлайн-статус бота ===
@bot.event
async def on_ready():
    print(f"✅ {bot.user} готов!")
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching,
        name="за пингом"
    ))


# Запуск
bot.run(TOKEN)
#понятно что нужно использовать env но для тестов сойдет
