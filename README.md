# LiveChat Plugin for Endstone

LiveChat is a plugin for Minecraft Bedrock Dedicated Servers (BDS) using the Endstone API (version 0.8). It integrates your Minecraft server with Discord, enabling seamless communication between in-game chat and a specified Discord channel. The plugin supports staff chat, player join/quit/death notifications, real-time server status updates, and customizable translations.

## Features

- **Discord Chat Integration**: Syncs in-game chat with a Discord channel, allowing messages to be sent between Minecraft and Discord.
- **Staff Chat**: Toggleable staff-only chat mode using the `/staffchat` (or `/sc`) command, accessible to operators or players with the `staffchat.use` permission.
- **Player Notifications**: Sends messages to Discord for player join (`🟢 <player> joined`), quit (`🔴 <player> left`), and death (`☠️ <player> died`) events.
- **Server Status**: Displays real-time TPS and online player count in the Discord bot's status, updated every 10 seconds, with translatable format.
- **Discord /list Command**: Shows the list of online players and current TPS in an embed via the `/list` command in Discord.
- **Translations**: Supports multiple languages (English and Russian by default) configurable in `config.json`.

## Installation

1. Place the plugin in the `plugins` folder of your Bedrock Dedicated Server.
2. Configure the plugin by editing the `config.json` file in the plugin's data folder.

## Configuration

The plugin generates a `config.json` file in the `plugins/LiveChat` directory upon first load. Update it with your Discord bot token, channel ID, and preferred language:

```json
{
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