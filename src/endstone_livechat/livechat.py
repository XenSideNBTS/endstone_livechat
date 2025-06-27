from endstone.plugin import Plugin
from endstone.event import event_handler
from endstone._internal.endstone_python import PlayerChatEvent, PlayerJoinEvent, PlayerQuitEvent, PlayerDeathEvent
from endstone.command import *
from endstone import ColorFormat
from endstone import Player
from discord.ext import commands
from discord import app_commands
import discord
import json
import asyncio
from pathlib import Path
import threading

class LiveChat(Plugin):
    api_version = "0.8"
    commands = {
        "staffchat": {
            "description": "Toggle staff chat mode.",
            "usages": ["/staffchat"],
            "aliases": ["sc"],
            "permissions": ["staffchat.use"],
        },
    }
    permissions = {
        "staffchat.use": {
            "description": "Allow users to talk in Staff Chat.",
            "default": "op",
        },
    }

    def __init__(self):
        super().__init__()
        self.bot = None
        self.bot_thread = None
        self.channel = None
        self.sc = []
        self.cf = ColorFormat
        self.translations = {}

    def on_load(self):
        config_path = Path(self.data_folder) / "config.json"
        default_config = {
            "token": "YOUR_DISCORD_BOT_TOKEN",
            "channel_id": 123456789,
            "language": "en",
            "translations": {
                "en": {
                    "staffchat_enabled": "&bAll messages will now be sent to staff chat",
                    "staffchat_disabled": "&cYour messages will no longer be sent to staff chat",
                    "not_player": "&cYou must be a player to run this command",
                    "player_list_title": "Player List",
                    "no_players": "No players are currently online",
                    "online_count": "Online: {count}",
                    "current_tps": "Current TPS",
                    "player_joined": "🟢 **{player}** joined the server",
                    "player_left": "🔴 **{player}** left",
                    "player_died": "☠️ **{player}** died",
                    "staffchat_message": "&6&l[Staff]&r&6 {name}&e > &y{message}",
                    "discord_message": "&b[Discord] {author}&r: {content}",
                    "bot_login": "Discord bot logged in as {user}",
                    "channel_error": "Could not find specified channel!",
                    "discord_error": "Failed to send message to Discord: {error}",
                    "bot_error": "Failed to start Discord bot: {error}"
                },
                "ru": {
                    "staffchat_enabled": "&bВсе сообщения теперь будут отправляться в чат персонала",
                    "staffchat_disabled": "&cВаши сообщения больше не будут отправляться в чат персонала",
                    "not_player": "&cВы должны быть игроком, чтобы выполнить эту команду",
                    "player_list_title": "Список игроков",
                    "no_players": "На сервере сейчас нет игроков",
                    "online_count": "Онлайн: {count}",
                    "current_tps": "Текущий TPS",
                    "player_joined": "🟢 **{player}** зашёл на сервер",
                    "player_left": "🔴 **{player}** вышел",
                    "player_died": "☠️ **{player}** умер",
                    "staffchat_message": "&6&l[Staff]&r&6 {name}&e > &y{message}",
                    "discord_message": "&b[Discord] {author}&r: {content}",
                    "bot_login": "Discord бот вошёл как {user}",
                    "channel_error": "Не удалось найти указанный канал!",
                    "discord_error": "Не удалось отправить сообщение в Discord: {error}",
                    "bot_error": "Не удалось запустить Discord бот: {error}"
                }
            }
        }
        if not config_path.exists():
            self.save_config(default_config)
        self._config = self.load_config()
        self.translations = self._config["translations"].get(self._config["language"], self._config["translations"]["en"])

        intents = discord.Intents.default()
        intents.message_content = True
        self.bot = commands.Bot(command_prefix="!", intents=intents)

        @self.bot.tree.command(name="list", description="Shows the list of online players")
        async def player_list(interaction: discord.Interaction):
            players = list(self.server.online_players)
            if not players:
                embed = discord.Embed(
                    title=self.translations["player_list_title"],
                    description=self.translations["no_players"],
                    color=discord.Color.green()
                )
            else:
                player_names = "\n".join([f"• {player.name}" for player in players])
                embed = discord.Embed(
                    title=self.translations["player_list_title"],
                    description=f"{self.translations['online_count'].format(count=len(players))}\n\n{player_names}",
                    color=discord.Color.green()
                )
            embed.add_field(name=self.translations["current_tps"], value=f"{self.get_tps():.2f}", inline=False)
            await interaction.response.send_message(embed=embed)

        @self.bot.event
        async def on_ready():
            self.logger.info(self.translations["bot_login"].format(user=self.bot.user))
            self.channel = self.bot.get_channel(self._config["channel_id"])
            if not self.channel:
                self.logger.error(self.translations["channel_error"])
            await self.bot.tree.sync()
            self.bot.loop.create_task(self.update_status())

        @self.bot.event
        async def on_message(message):
            if message.author == self.bot.user:
                return

            if message.channel.id == self._config["channel_id"]:
                try:
                    for player in self.server.online_players:
                        player.send_message(self.translations["discord_message"].format(author=message.author.name, content=message.content))
                except Exception as e:
                    self.logger.error(self.translations["discord_error"].format(error=e))

    def on_enable(self):
        self.logger.info("LiveChat plugin enabled!")
        self.register_events(self)
        self.bot_thread = threading.Thread(target=self._run_bot, daemon=True)
        self.bot_thread.start()

    def on_disable(self):
        self.logger.info("LiveChat plugin disabled!")
        if self.bot:
            asyncio.run_coroutine_threadsafe(self.bot.close(), self.bot.loop)
        if self.bot_thread:
            self.bot_thread.join(timeout=1.0)

    def _run_bot(self):
        try:
            self.bot.run(self._config["token"])
        except Exception as e:
            self.logger.error(self.translations["bot_error"].format(error=e))

    def on_command(self, sender: CommandSender, command: Command, args: list[str]) -> bool:
        if command.name == "staffchat":
            if isinstance(sender, Player):
                if sender.name not in self.sc:
                    self.sc.append(str(sender.name))
                    sender.send_message(self.translations["staffchat_enabled"])
                    return True
                else:
                    self.sc.remove(str(sender.name))
                    sender.send_message(self.translations["staffchat_disabled"])
            else:
                sender.send_error_message(self.translations["not_player"])
                return False
        return True

    def check_sc(self, uname):
        return uname in self.sc

    def broadcast_staff(self, player, msg):
        name = player.name
        mes = self.translations["staffchat_message"].format(name=name, message=msg)
        self.server.broadcast(mes, "staffchat.use")

    @event_handler
    def on_player_chat(self, event: PlayerChatEvent):
        if not self.channel:
            return

        player_name = event.player.name
        message = event.message

        if self.check_sc(player_name):
            self.broadcast_staff(event.player, message)
            event.is_cancelled = True
            return

        async def send_message():
            try:
                await self.channel.send(f"**{player_name}**: {message.replace('@', '')}")
            except Exception as e:
                self.logger.error(self.translations["discord_error"].format(error=e))

        if self.bot and self.bot.loop:
            asyncio.run_coroutine_threadsafe(send_message(), self.bot.loop)

    @event_handler
    def on_player_join(self, event: PlayerJoinEvent):
        if not self.channel:
            return

        player_name = event.player.name

        async def send_join():
            try:
                await self.channel.send(self.translations["player_joined"].format(player=player_name))
            except Exception as e:
                self.logger.error(self.translations["discord_error"].format(error=e))

        if self.bot and self.bot.loop:
            asyncio.run_coroutine_threadsafe(send_join(), self.bot.loop)

    @event_handler
    def on_player_quit(self, event: PlayerQuitEvent):
        if not self.channel:
            return

        player_name = event.player.name
        if self.check_sc(player_name):
            self.sc.remove(player_name)

        async def send_quit():
            try:
                await self.channel.send(self.translations["player_left"].format(player=player_name))
            except Exception as e:
                self.logger.error(self.translations["discord_error"].format(error=e))

        if self.bot and self.bot.loop:
            asyncio.run_coroutine_threadsafe(send_quit(), self.bot.loop)

    @event_handler
    def on_player_death(self, event: PlayerDeathEvent):
        if not self.channel:
            return

        player_name = event.player.name

        async def send_death():
            try:
                await self.channel.send(self.translations["player_died"].format(player=player_name))
            except Exception as e:
                self.logger.error(self.translations["discord_error"].format(error=e))

        if self.bot and self.bot.loop:
            asyncio.run_coroutine_threadsafe(send_death(), self.bot.loop)

    def load_config(self):
        config_path = Path(self.data_folder) / "config.json"
        with open(config_path, "r") as f:
            return json.load(f)

    def save_config(self, config):
        config_path = Path(self.data_folder) / "config.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w") as f:
            json.dump(config, f, indent=4)

    def get_tps(self):
        return self.server.current_tps

    def get_player_count(self):
        return len(self.server.online_players)

    async def update_status(self):
        while not self.bot.is_closed():
            tps = self.get_tps()
            players = self.get_player_count()
            status = f"TPS: {tps:.2f} | Players: {players}"
            await self.bot.change_presence(activity=discord.Game(name=status))
            await asyncio.sleep(10)