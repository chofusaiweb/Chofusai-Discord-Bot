import asyncio
import os

import discord

# import sentry_sdk
from discord.ext import commands

from utils.logger import getMyLogger

if not __debug__:
    from dotenv import load_dotenv

    load_dotenv()


class Bot(commands.Bot):
    def __init__(self, **kwargs):
        # self.init_sentry()
        self.logger = getMyLogger(__name__)
        self.app_cmd_sync_target = discord.Object(int(os.environ["GUILD_ID"]))

        # set intents
        intents = discord.Intents.all()
        intents.typing = False

        # info params
        self.failed_extensions: list[str] = []
        self.failed_views: list[str] = []
        self.synced_cmd_mention: list[str] = []

        super().__init__(
            command_prefix="!mc ",
            intents=intents,
            **kwargs,
        )

    async def setup_hook(self) -> None:
        await self.load_exts()
        await self.sync_app_commands()
        await self.setup_views()

    async def on_ready(self) -> None:
        self.print_status()

    async def load_exts(self, reload: bool = False) -> None:
        ext_paths = ["src.cogs.cog"]
        if ext_paths is None:
            return

        for ext in ext_paths:
            try:
                await self.load_extension(ext)
            except Exception as e:
                self.logger.exception(f"Failed to load {ext}", exc_info=e)
                self.failed_extensions.append(ext)
        return

    async def sync_app_commands(self) -> None:
        try:
            synced_cmd = await self.tree.sync(guild=self.app_cmd_sync_target)
        except Exception as e:
            self.logger.exception("Failed to sync application commands", exc_info=e)
            self.synced_cmd_mention = []
        else:
            self.logger.info("Application commands synced successfully")
            self.synced_cmd_mention = [c.mention for c in synced_cmd]

    async def setup_views(self) -> None:
        pass

    def print_status(self) -> None:
        self.logger.info(f"Logged in as {self.user} (ID: {self.user.id})")  # pyright: ignore
        self.logger.info(f"Connected to {len(self.guilds)} guilds")  # pyright: ignore
        self.logger.info("Bot is ready")

    # def init_sentry(self) -> None:
    #     sentry_sdk.init(
    #         dsn=os.environ["SENTRY_DSN"],
    #         # Set traces_sample_rate to 1.0 to capture 100%
    #         # of transactions for performance monitoring.
    #         # We recommend adjusting this value in production.
    #         traces_sample_rate=1.0,
    #     )

    def run(self) -> None:
        try:
            asyncio.run(self.runner())
        except Exception as e:
            self.logger.critical("SystemExit Detected, shutting down...", exc_info=e)
            asyncio.run(self.shutdown(status=1))
            return

    async def runner(self) -> None:
        async with self:
            await self.start(os.environ["DISCORD_BOT_TOKEN"])

    async def shutdown(self, status: int = 0) -> None:
        import sys

        # from sentry_sdk import Hub
        # # shutdown Sentry
        # client = Hub.current.client
        # if client is not None:
        #     client.close(timeout=2.0)

        self.logger.info("Shutting down...")
        await self.close()
        sys.exit(status)
