import irc.client
import json
from datetime import datetime
import os
import logging
import signal
import sys
from typing import Optional
import time
import requests
from dotenv import load_dotenv

class IRCClient:
    def __init__(self):
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

        # Load environment variables from .env file
        load_dotenv()

        self.irc_config = {
            'server': "irc.ppy.sh",
            'port': 6667,
            'username': os.getenv("IRC_USERNAME"),
            'password': os.getenv("IRC_PASSWORD"),
            'channel': "#osu"
        }

        self.logstash_url = "http://logstash:5044"

        self.client = irc.client.Reactor()
        self.connection: Optional[irc.client.ServerConnection] = None
        self.running = True

    def on_message(self, connection, event):
        try:
            username = event.source.split("!")[0]
            message = event.arguments[0]
            timestamp = datetime.utcnow().isoformat()

            payload = {
                "username": username,
                "message": message,
                "timestamp": timestamp,
                "channel": self.irc_config['channel']
            }

            response = requests.post(self.logstash_url, json=payload)
            response.raise_for_status()

            logging.info(f"Message sent to Logstash: {username}: {message}")

        except Exception as e:
            logging.error(f"Error processing message: {e}")

    def on_connect(self, connection, event):
        logging.info(f"Connected to {self.irc_config['server']}")
        connection.join(self.irc_config['channel'])

    def on_disconnect(self, connection, event):
        logging.warning("Disconnected from server")
        if self.running:
            self.reconnect()

    def reconnect(self, max_attempts=5):
        attempts = 0
        while attempts < max_attempts and self.running:
            try:
                logging.info(f"Attempting to reconnect (attempt {attempts + 1})")
                self.connect()
                return True
            except Exception as e:
                logging.error(f"Reconnection failed: {e}")
                attempts += 1
                time.sleep(5)
        return False

    def connect(self):
        self.connection = self.client.server().connect(
            self.irc_config['server'],
            self.irc_config['port'],
            self.irc_config['username'],
            password=self.irc_config['password']
        )
        self.connection.add_global_handler("welcome", self.on_connect)
        self.connection.add_global_handler("pubmsg", self.on_message)
        self.connection.add_global_handler("disconnect", self.on_disconnect)

    def signal_handler(self, signum, frame):
        logging.info("Shutdown signal received")
        self.running = False
        if self.connection:
            self.connection.disconnect("Bot shutting down")
        sys.exit(0)

    def run(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        try:
            self.connect()
            while self.running:
                self.client.process_once(timeout=0.2)
        except Exception as e:
            logging.error(f"Fatal error: {e}")
            self.running = False


if __name__ == "__main__":
    client = IRCClient()
    client.run()