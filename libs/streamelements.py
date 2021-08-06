import os
from selenium import webdriver

class StreamElements(object):
    def __init__(self, config:str) -> None:
        super().__init__()
        self.config = config
        self.channel = config["CHANNEL"]
        
    
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
        for item in public_store_items[1:]:
            newItem = {}
            try:
                strItem = str(item.text).split("\n")
                newItem["play_arrow"] = strItem[0]
                if strItem[0] != "play_arrow":
                    for key in range(1, len(strItem), 2):
                        if key < len(strItem)-1:
                            tag = strItem[key]
                            value = strItem[key+1]
                            newItem[tag] = value
                if "|" in newItem["play_arrow"]:
                    self.__screenshotItem(item, newItem["play_arrow"])
                allItems.append(newItem)
            except Exception as err:
                print(err)
                ...
        return allItems

    def __screenshotItem(self, element, elementName:str):
        if os.path.isfile(f"{elementName}.jpg"): os.remove(f"{elementName}.jpg")
        element.screenshot(f"{elementName}.jpg")

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
