from libs.configuration import Configuration
from libs.discord_wb import Discord
from libs.streamelements import StreamElements
from time import sleep
from datetime import date, datetime

if __name__ == "__main__":
    config = Configuration()
    discord = Discord(url=config.App["DISCORD"]["WEBHOOK"])
    stream = StreamElements(config=config.App["STREAMELEMENTS"])

    while True:
        items = stream.execute()
        if items:
            discord.createPosts(items=items)
        print(
            f"{datetime.now().isoformat()} | {len(items)} ITEM(S) DISPONIVEL(EIS) NA LOJA DO {config.App['STREAMELEMENTS']['CHANNEL'].upper()}")
        sleep(config.App["STREAMELEMENTS"]["INTERVAL"]*60)
