from endstone.plugin import Plugin
from endstone.event import event_handler
from endstone._internal.endstone_python import PlayerChatEvent
import requests
import json
from pathlib import Path

class LiveChat(Plugin):
    api_version = "0.5"

    def on_load(self):
        self.logger.info(f"Data folder: {self.data_folder}")
        config_path = Path(self.data_folder) / "config.yml"
        default_config = {
            "webhook_url": "YOUR_DISCORD_WEBHOOK_URL",
            "avatar_url": "https://example.com/default_avatar.png"
        }
        if not config_path.exists():
            self.save_config(default_config)
        self._config = self.load_config()
    
    def on_enable(self):
        self.logger.info("LiveChat plugin enabled!")
        self.register_events(self)
    
    def on_disable(self):
        self.logger.info("LiveChat plugin disabled!")
    
    @event_handler
    def on_player_chat(self, event: PlayerChatEvent):
        webhook_url = self._config.get("webhook_url")
        avatar_url = self._config.get("avatar_url")
        player_name = event.player.name
        message = event.message
        payload = {
            "content": f"**{player_name}**: {message}",
            "avatar_url": avatar_url
        }
        
        try:
            response = requests.post(webhook_url, data=json.dumps(payload), headers={"Content-Type": "application/json"})
            response.raise_for_status()
        except requests.RequestException:
            self.logger.error("Failed to send message to Discord webhook")
    
    def load_config(self):
        config_path = Path(self.data_folder) / "config.yml"
        with open(config_path, "r") as f:
            return json.load(f)
    
    def save_config(self, config):
        config_path = Path(self.data_folder) / "config.yml"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w") as f:
            json.dump(config, f, indent=4)
