from discord_webhook import DiscordWebhook, DiscordEmbed
from queue import Queue
import threading
import os
from time import sleep

from libs.configuration import Configuration
from libs.streamelements import Product


class Discord(object):

    def __init__(self, url: str):
        self.client = DiscordWebhook(url)
        self.__config = Configuration().App
        self.__channel = self.__config['STREAMELEMENTS']['CHANNEL']
        self.__path_img = "./images/"

    def createPost(self, item: Product):
        newPost = DiscordEmbed(
            title=item.name, description='Checkout this new item on Store', color='03b2f8')
        newPost.set_url(f"https://streamelements.com/{self.__channel}/store")
        newPost.set_author(name="Junior Saldanha | BOT StreamElements",
                           icon_url="https://cdn.streamelements.com/assets/homepage/SE_logo_396x309px_ground_control_page%403x.png")
        newPost.add_embed_field(name="Name", value=item.name, inline=True)
        newPost.add_embed_field(
            name="Quantity", value=item.quantity, inline=True)
        newPost.add_embed_field(name="Cost", value=item.cost, )
        if os.path.isfile(f"{self.__path_img}{item.id}.jpg"):
            with open(f"{self.__path_img}{item.id}.jpg", "rb") as f:
                self.client.add_file(
                    file=f.read(), filename=f"{self.__path_img}{item.id}.jpg")
        newPost.set_footer(text="Go get if u liked. 🤖")
        newPost.set_timestamp()
        self.client.add_embed(newPost)
        self.client.execute()
        self.client.remove_embeds()
        self.client.remove_files()

    def createPosts(self, items: list):
        for item in items:
            self.createPost(item)
            self.__remove_image(item)
            sleep(3)

    def __remove_image(self, item: Product):
        if os.path.isfile(f"{self.__path_img}{item.id}.jpg"):
            os.remove(f"{self.__path_img}{item.id}.jpg")

    def __remove_all_images(self):
        for item in os.listdir("./"):
            if item.endswith(".jpg"):
                os.remove(item)
