require("dotenv").config();
const { Client, GatewayIntentBits, EmbedBuilder, ActivityType } = require("discord.js");
const { cpuUsage, freemem, totalmem } = require("systeminformation");
const { ping } = require("ping");
const { execSync } = require("child_process");

const TOKEN = process.env.DISCORD_TOKEN;

if (!TOKEN) {
  console.error("❌ Ошибка: DISCORD_TOKEN не найден в .env файле!");
  process.exit(1);
}

const client = new Client({
  intents: [GatewayIntentBits.Guilds, GatewayIntentBits.MessageContent],
});

const startTime = Date.now();

const TEST_SITES = [
  "google.com",
  "discord.com",
  "github.com",
  "yandex.ru",
  "cloudflare.com",
];

client.on("ready", () => {
  console.log(`✅ ${client.user.tag} успешно запущен!`);
  client.user.setPresence({
    activities: [{ name: "!ping | Тест пинга", type: ActivityType.Playing }],
    status: "online",
  });
});

// ── /ping ──────────────────────────────────────────────────────────────
client.on("interactionCreate", async (interaction) => {
  if (!interaction.isChatInputCommand()) return;

  const { commandName } = interaction;

  if (commandName === "ping") {
    await interaction.deferReply();

    const wsPing = Math.round(client.ws.ping);
    const cmdStart = Date.now();

    const tempMsg = await interaction.followUp("⏳");
    await sleep(100);
    try {
      await tempMsg.delete();
    } catch {
      /* already gone */
    }
    const cmdPing = Date.now() - cmdStart;

    const apiStart = Date.now();
    let apiPing;
    try {
      await client.fetchUser(client.user.id);
      apiPing = Date.now() - apiStart;
    } catch {
      apiPing = null;
    }

    const status =
      wsPing < 100
        ? "🟢 Отлично"
        : wsPing < 200
          ? "🟡 Удовлетворительно"
          : "🔴 Высокий";

    const uptimeMs = Date.now() - client.readyTimestamp;
    const uptimeStr = formatUptime(uptimeMs);

    const embed = new EmbedBuilder()
      .setTitle("🏓 Состояние бота")
      .setColor(0x5865f2)
      .setTimestamp()
      .addFields(
        {
          name: "📡 WebSocket пинг",
          value: `\`\`\`${wsPing.toFixed(1)} мс\`\`\``,
          inline: true,
        },
        {
          name: "💬 Отклик команды",
          value: `\`\`\`${cmdPing.toFixed(1)} мс\`\`\``,
          inline: true,
        },
        {
          name: "📤 API пинг",
          value: apiPing !== null ? `\`\`\`${apiPing.toFixed(1)} мс\`\`\`` : "\`\`\`⚠️ Ошибка\`\`\`",
          inline: true,
        },
        { name: "📊 Статус", value: status, inline: true },
        { name: "⏱️ Аптайм", value: `\`\`\`${uptimeStr}\`\`\``, inline: true },
        {
          name: "🖥️ Серверов",
          value: `\`\`\`${client.guilds.cache.size.toLocaleString()}\`\`\``,
          inline: true,
        },
      )
      .setThumbnail(client.user.displayAvatarURL())
      .setFooter({
        text: "PingTest Bot • Диагностика",
        iconURL: client.user.displayAvatarURL(),
      });

    return interaction.followUp({ embeds: [embed] });
  }

  // ── /system ──────────────────────────────────────────────────────────
  if (commandName === "system") {
    await interaction.deferReply();

    const cpu = await cpuUsage();
    const mem = await getMemoryInfo();
    const disk = getDiskInfo("/");

    const embed = new EmbedBuilder()
      .setTitle("🖥️ Состояние сервера")
      .setColor(0x5865f2)
      .setTimestamp()
      .addFields(
        {
          name: "⚡ CPU",
          value: `\`\`\`${cpu.currentLoad.toFixed(1)}%\`\`\``,
          inline: false,
        },
        {
          name: "💾 RAM",
          value: `\`\`\`${mem.usedGb.toFixed(1)} ГБ / ${mem.totalGb.toFixed(1)} ГБ (${mem.percent}%)\`\`\``,
          inline: false,
        },
        {
          name: "💽 Диск",
          value: `\`\`\`${disk.usedGb.toFixed(1)} ГБ / ${disk.totalGb.toFixed(1)} ГБ (${disk.percent}%)\`\`\``,
          inline: false,
        },
      )
      .setFooter({
        text: "PingTest Bot • Мониторинг",
        iconURL: client.user.displayAvatarURL(),
      });

    return interaction.followUp({ embeds: [embed] });
  }

  // ── /pingtest ────────────────────────────────────────────────────────
  if (commandName === "pingtest") {
    await interaction.deferReply();

    const results = [];

    for (const site of TEST_SITES) {
      try {
        const res = await ping(site);
        const ms = res.avg !== undefined ? parseFloat(res.avg) : null;

        if (ms !== null && !isNaN(ms)) {
          const emoji = ms < 100 ? "🟢" : ms < 300 ? "🟡" : "🔴";
          results.push(`${emoji} \`${site.padEnd(15)}\` → \`${ms.toFixed(1).padStart(6)} мс\``);
        } else {
          results.push(`🔴 \`${site.padEnd(15)}\` → \`Таймаут\``);
        }
      } catch {
        results.push(`❌ \`${site.padEnd(15)}\` → \`Ошибка\``);
      }
    }

    const embed = new EmbedBuilder()
      .setTitle("🌐 Тест пинга до сайтов")
      .setDescription(results.join("\n"))
      .setColor(0x5865f2)
      .setTimestamp()
      .setFooter({
        text: "PingTest Bot • Сеть",
        iconURL: client.user.displayAvatarURL(),
      });

    return interaction.followUp({ embeds: [embed] });
  }

  // ── /uptime ──────────────────────────────────────────────────────────
  if (commandName === "uptime") {
    await interaction.deferReply();

    const uptimeMs = Date.now() - client.readyTimestamp;
    const uptimeStr = formatUptime(uptimeMs);

    const embed = new EmbedBuilder()
      .setTitle("⏱️ Аптайм бота")
      .setDescription(`Бот работает: **${uptimeStr}**`)
      .setColor(0x5865f2)
      .setTimestamp()
      .setFooter({
        text: "PingTest Bot",
        iconURL: client.user.displayAvatarURL(),
      });

    return interaction.followUp({ embeds: [embed] });
  }
});

// ── Register slash commands on ready ────────────────────────────────────
client.once("ready", async () => {
  try {
    await client.application.commands.set([
      {
        name: "ping",
        description: "🏓 Проверить пинг и состояние бота",
      },
      {
        name: "system",
        description: "🖥️ Показать состояние сервера",
      },
      {
        name: "pingtest",
        description: "🌐 Проверить пинг до сайтов",
      },
      {
        name: "uptime",
        description: "⏱️ Показать аптайм бота",
      },
    ]);
    console.log("✅ Slash-команды зарегистрированы.");
  } catch (err) {
    console.error("❌ Ошибка регистрации команд:", err);
  }
});

// ── Helpers ─────────────────────────────────────────────────────────────
function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

function formatUptime(ms) {
  const totalSec = Math.floor(ms / 1000);
  const sec = totalSec % 60;
  const mins = Math.floor(totalSec / 60) % 60;
  const hours = Math.floor(totalSec / 3600) % 24;
  const days = Math.floor(totalSec / 86400);

  if (days > 0) return `${days}д ${hours}ч`;
  return `${hours}ч ${mins}м`;
}

function getMemoryInfo() {
  const total = totalmem();
  const free = freemem();
  const used = total - free;
  const percent = ((used / total) * 100).toFixed(1);
  return {
    usedGb: used / 1024 ** 3,
    totalGb: total / 1024 ** 3,
    percent,
  };
}

function getDiskInfo(mountPoint) {
  try {
    const output = execSync(`df -B1 ${mountPoint} | tail -1`).toString().trim();
    const parts = output.split(/\s+/);
    const total = parseInt(parts[1], 10);
    const used = parseInt(parts[2], 10);
    const percent = parseFloat(parts[4]);
    return {
      usedGb: used / 1024 ** 3,
      totalGb: total / 1024 ** 3,
      percent,
    };
  } catch {
    return { usedGb: 0, totalGb: 0, percent: 0 };
  }
}

// ── Login ───────────────────────────────────────────────────────────────
client.login(TOKEN);
