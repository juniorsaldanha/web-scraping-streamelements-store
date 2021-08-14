from discord_webhook import DiscordWebhook, DiscordEmbed
from queue import Queue
import threading, os
from time import sleep

import selenium
from libs.configuration import Configuration


class Discord(object):
    
    def __init__(self, url:str):
        self.client = DiscordWebhook(url)
        self.queue = Queue()
        threading.Thread(target=self.__sync_queue,)
        self.__config = Configuration().App
        self.__channel = self.__config['STREAMELEMENTS']['CHANNEL']

    def createPost(self, item:dict):
        title = "📈 📈 SKIN | "+item['play_arrow'] if "|" in item['play_arrow'] else 'New Item'
        newPost = DiscordEmbed(title=title, description='Checkout this new item on Store', color='03b2f8')
        newPost.set_url(f"https://streamelements.com/{self.__channel}/store")
        if "SKIN" in title: newPost.set_thumbnail(url="https://img.icons8.com/ios/250/000000/price-tag.png")
        newPost.set_author(name="Junior Saldanha | BOT StreamElements", icon_url="https://cdn.streamelements.com/assets/homepage/SE_logo_396x309px_ground_control_page%403x.png")
        newPost.add_embed_field(name="Item", value=item['play_arrow'])
        newPost.add_embed_field(name="Quantity", value=item['shopping_basket'])
        newPost.add_embed_field(name="Value", value=item['monetization_on'], )
        if os.path.isfile(f"{str(item['play_arrow']).strip().lower()}.jpg"):
            with open(f"{str(item['play_arrow']).strip().lower()}.jpg", "rb") as f:
                self.client.add_file(file=f.read(), filename=f"{item['play_arrow']}.jpg")
        newPost.set_footer(text="Go get if u liked. 🤖")
        newPost.set_timestamp()
        self.client.add_embed(newPost)
        response = self.client.execute()
        self.client.remove_embeds()
        self.client.remove_files()
        if not response.status_code == 200: self.queue.put(newPost)
    
    def createPosts(self, items:list):
        for item in items:
                self.__print_item(item)
                self.createPost(item)
                self.__remove_image(item['play_arrow'])
                sleep(3)

    def __print_item(self, item:dict):
        print(
f"""
Item: {item['play_arrow']}
\tQuantity: {item['shopping_basket']}
\tValue: {item['monetization_on']}\n
"""
        )

    def __remove_image(self, file:str):
        if os.path.isfile(f"{file.strip().lower()}.jpg"): os.remove(f"{file.strip().lower()}.jpg")

    def __remove_all_images(self):
        for item in os.listdir("./"):
            if item.endswith(".jpg"):
                os.remove(item)

    def __sync_queue(self,):
        if self.queue.qsize() > 0:
            oldPost = self.queue.get()
            oldPost.set_footer(text="Go get if u liked. 🤖 but go faster because this is a old product that was stuck on bot!")