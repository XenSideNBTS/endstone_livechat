from endstone.plugin import Plugin
from endstone.event import EventPriority, event_handler
from endstone.game import Game
from endstone.player import Player
import requests
import json
from pathlib import Path

class LiveChat(Plugin):
    def on_load(self):
        config_path = Path(self.data_folder) / "config.yml"
        default_config = {"webhook_url": "YOUR_DISCORD_WEBHOOK_URL"}
        if not config_path.exists():
            self.save_config(default_config)
        self._config = self.load_config()
    
    def on_enable(self):
        self.logger.info("LiveChat plugin enabled!")
    
    def on_disable(self):
        self.logger.info("LiveChat plugin disabled!")
    
    @event_handler(EventPriority.NORMAL)
    def on_player_chat(self, game: Game, player: Player, message: str):
        webhook_url = self._config.get("webhook_url")
        player_name = player.name
        payload = {
            "content": f"**{player_name}**: {message}"
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
        with open(config_path, "w") as f:
            json.dump(config, f, indent=4)

def plugin():
    return LiveChat()
