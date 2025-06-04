import os
import json
from endstone.command import Command, CommandSender
from endstone.plugin import Plugin
from endstone import Player
from endstone.event import event_handler, PlayerChatEvent
import requests

class livechat(Plugin):
    def __init__(self):
        self.plugin_dir = "plugins/livechat"
        self.config_file = os.path.join(self.plugin_dir, "config.json")
        self.default_config = {
            "webhook_url": "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_TOKEN",
            "webhook_username": "Minecraft Chat",
            "webhook_avatar": "https://i.imgur.com/JnX9yFq.png",
            "format": "**{player}**: {message}"
        }
        self.config = None

    def on_enable(self) -> None:
        self.setup_config()
        self.logger.info("LiveChat enabled! Chat messages will be sent to Discord.")
        self.register_events(self)

    def setup_config(self):
        if not os.path.exists(self.plugin_dir):
            os.makedirs(self.plugin_dir)
        
        if not os.path.exists(self.config_file):
            with open(self.config_file, 'w') as f:
                json.dump(self.default_config, f, indent=4)
            self.config = self.default_config
        else:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)

    def send_to_discord(self, player: Player, message: str):
        formatted_msg = self.config["format"].format(
            player=player.name,
            message=message
        )
        
        payload = {
            "content": formatted_msg,
            "username": self.config["webhook_username"],
            "avatar_url": self.config["webhook_avatar"]
        }
        
        try:
            requests.post(
                self.config["webhook_url"],
                json=payload,
                timeout=5
            )
        except Exception as e:
            self.logger.error(f"Error sending to Discord: {str(e)}")

    @event_handler
    def on_player_chat(self, event: PlayerChatEvent):
        self.send_to_discord(event.player, event.message)
