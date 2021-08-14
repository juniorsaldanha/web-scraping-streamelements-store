import os
from time import sleep, time
from selenium import webdriver
import requests

class StreamElements(object):
    def __init__(self, config:str) -> None:
        super().__init__()
        self.config = config
        self.channel = self.config["CHANNEL"]
        
    
    def __setup_chromedriver(self,):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--silent")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--whitelisted-ips")
        self.driver = webdriver.Chrome("chromedriver", options=chrome_options, )

    def __getPublicStoreItems(self,):
        self.__setup_chromedriver()
        self.driver.get(f"https://streamelements.com/{self.channel}/store")
        self.driver.implicitly_wait(8)
        public_store_items = self.driver.find_elements_by_tag_name('md-card')
        return public_store_items
    
    def __remove_all_images(self):
        for item in os.listdir("./"):
            if item.endswith(".jpg"):
                os.remove(item)

    def __parseStoreItems(self, public_store_items):
        self.__remove_all_images()
        while len(public_store_items) == 0: public_store_items = self.__getPublicStoreItems()
        allItems = []

        for item in public_store_items:
            try:
                newItem = {}
                strItem = str(item.text).split("\n")
                if strItem[0] == "play_arrow": strItem.pop(0)
                newItem["play_arrow"] = strItem[0]
                for key in range(1, len(strItem), 2):
                    if key < len(strItem)-1:
                        tag = strItem[key]
                        value = strItem[key+1]
                        newItem[tag] = value

                self.__screenshotItem(item, newItem["play_arrow"])
                if "shopping_basket" in newItem.keys():
                    for word in newItem["shopping_basket"].split(" "):
                        try:
                            if isinstance(int(word), int):
                                newItem["shopping_basket"] = newItem["shopping_basket"].split(" ")[0]
                                ...
                        except ValueError: ...
                    allItems.append(newItem)
            except Exception as err:
                print(err)
                ...
        return allItems

    def __screenshotItem(self, element, elementName:str):
        if os.path.isfile(f"{elementName.strip().lower()}.jpg"): os.remove(f"{elementName.strip().lower()}.jpg")
        src_img = element.find_element_by_tag_name('img').get_attribute("src")
        response = requests.get(src_img)
        if response.status_code == 200:
            with open(f"{elementName.strip().lower()}.jpg", 'wb') as f:
                f.write(response.content)
        return

    def run(self, onlyAvailable:bool = True, ):
        Allitems = self.__parseStoreItems(self.__getPublicStoreItems())
        filtedByStrings = []
        filtedByAvailable = []

        # Fazer list comprehension nos 2 for abaixo
        for item in Allitems:
            if not any(map(item["play_arrow"].__contains__, self.config["STRINGS_TO_REMOVE_ITEMS"])): filtedByStrings.append(item)
        if not onlyAvailable: return filtedByStrings
        for item in filtedByStrings:
            if onlyAvailable and item["shopping_basket"] != "Sold out":
                filtedByAvailable.append(item)
        self.driver.quit()
        self.driver = None
        return filtedByAvailable
