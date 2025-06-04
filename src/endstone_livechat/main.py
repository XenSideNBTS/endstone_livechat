import json
import os
from typing import Dict, Any
from endstone.plugin import Plugin
from endstone.event import event_handler, PlayerChatEvent
from endstone.command import Command, CommandSender
from endstone import ColorFormat
import requests

class LiveChat(Plugin):
    def __init__(self):
        super().__init__()
        self.config_path = os.path.join(self.data_folder, "config.json")
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        default_config = {
            "webhook_url": "YOUR_DISCORD_WEBHOOK_URL",
            "discord_name": "Minecraft Server",
            "discord_avatar": "https://i.imgur.com/4M34hi2.png",
            "chat_format": "**{player}**: {message}"
        }

        if not os.path.exists(self.config_path):
            os.makedirs(self.data_folder, exist_ok=True)
            with open(self.config_path, "w") as f:
                json.dump(default_config, f, indent=4)
            return default_config

        with open(self.config_path, "r") as f:
            return json.load(f)

    def save_config(self):
        with open(self.config_path, "w") as f:
            json.dump(self.config, f, indent=4)

    def send_to_discord(self, content: str):
        if not self.config["webhook_url"] or self.config["webhook_url"] == "YOUR_DISCORD_WEBHOOK_URL":
            self.logger.warning("Discord webhook URL not configured!")
            return

        payload = {
            "username": self.config["discord_name"],
            "avatar_url": self.config["discord_avatar"],
            "content": content
        }

        try:
            requests.post(self.config["webhook_url"], json=payload)
        except Exception as e:
            self.logger.error(f"Failed to send message to Discord: {str(e)}")

    @event_handler
    def on_player_chat(self, event: PlayerChatEvent):
        message = self.config["chat_format"].format(
            player=event.player.name,
            message=event.message
        )
        self.send_to_discord(message)

    def on_command(self, sender: CommandSender, command: Command, args: list[str]) -> bool:
        if command.name == "livechat":
            if not sender.has_permission("livechat.admin"):
                sender.send_message(f"{ColorFormat.RED}You don't have permission to use this command!")
                return True

            if not args:
                sender.send_message(
                    f"{ColorFormat.AQUA}LiveChat Configuration:\n"
                    f"{ColorFormat.WHITE}Webhook URL: {ColorFormat.MATERIAL_AMETHYST}{self.config['webhook_url']}\n"
                    f"{ColorFormat.WHITE}Discord Name: {ColorFormat.MATERIAL_AMETHYST}{self.config['discord_name']}\n"
                    f"{ColorFormat.WHITE}Discord Avatar: {ColorFormat.MATERIAL_AMETHYST}{self.config['discord_avatar']}\n"
                    f"{ColorFormat.WHITE}Chat Format: {ColorFormat.MATERIAL_AMETHYST}{self.config['chat_format']}\n\n"
                    f"{ColorFormat.WHITE}Usage: /livechat <seturl|setname|setavatar|setformat> <value>"
                )
                return True

            subcommand = args[0].lower()
            if subcommand == "seturl" and len(args) > 1:
                self.config["webhook_url"] = args[1]
                self.save_config()
                sender.send_message(f"{ColorFormat.GREEN}Discord webhook URL updated!")
                return True

            elif subcommand == "setname" and len(args) > 1:
                self.config["discord_name"] = " ".join(args[1:])
                self.save_config()
                sender.send_message(f"{ColorFormat.GREEN}Discord name updated!")
                return True

            elif subcommand == "setavatar" and len(args) > 1:
                self.config["discord_avatar"] = args[1]
                self.save_config()
                sender.send_message(f"{ColorFormat.GREEN}Discord avatar URL updated!")
                return True

            elif subcommand == "setformat" and len(args) > 1:
                self.config["chat_format"] = " ".join(args[1:])
                self.save_config()
                sender.send_message(f"{ColorFormat.GREEN}Chat format updated!")
                return True

            else:
                sender.send_message(f"{ColorFormat.RED}Invalid subcommand or missing arguments!")
                return True

        return False

    def on_enable(self) -> None:
        self.logger.info("LiveChat plugin enabled!")
        if self.config["webhook_url"] == "YOUR_DISCORD_WEBHOOK_URL":
            self.logger.warning("Please configure the Discord webhook URL in the config file!")

    def on_disable(self) -> None:
        self.logger.info("LiveChat plugin disabled!")
