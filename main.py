from src.bot import Bot

if not __debug__:
    from dotenv import load_dotenv

    load_dotenv()

if __name__ == "__main__":
    bot = Bot()
    bot.runner()
