import os
import requests
from pydantic import BaseModel
from typing import List, Optional


class Product(BaseModel):
    id: str
    name: str
    description: str
    cost: int
    quantity: int
    thumbnail: str
    categoryName: Optional[str]


class StreamElements(object):
    def __init__(self, config: str) -> None:
        super().__init__()
        self.config = config
        self.channel = self.config["CHANNEL"]
        self.filters = self.config["STRINGS_TO_REMOVE_ITEMS"]

    def execute(self,):
        self.__getIdChannel(self.channel)
        return self.__getItems()

    def __getIdChannel(self, channel):  # sourcery skip: raise-specific-error
        url = f"https://api.streamelements.com/kappa/v2/channels/{channel}"

        payload = ""
        headers = {
            "authority": "api.streamelements.com",
            "accept": "application/json, text/plain, */*",
            "accept-language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "cache-control": "no-cache",
            "origin": "https://streamelements.com",
            "pragma": "no-cache",
            "referer": "https://streamelements.com/",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "sec-gpc": "1",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36"
        }

        response = requests.request(
            "GET", url, data=payload, headers=headers).json()
        if "statusCode" in response.keys():
            raise Exception(response)
        self.channel_id = response["_id"]

    def __getItems(self,):
        public_store_items = []

        url = "https://api.streamelements.com/kappa/v2/store/5cc799026e852d26fcf16717/items"

        querystring = {"source": "website"}

        payload = ""
        headers = {
            "authority": "api.streamelements.com",
            "accept": "application/json, text/plain, */*",
            "accept-language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "cache-control": "no-cache",
            "origin": "https://streamelements.com",
            "pragma": "no-cache",
            "referer": "https://streamelements.com/",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "sec-gpc": "1",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36"
        }

        response = requests.request(
            "GET", url, data=payload, headers=headers, params=querystring)
        for product in response.json():
            if product["enabled"] and product["quantity"]["current"] > 0:
                product["quantity"] = product["quantity"]["current"]
                product["id"] = product["_id"]
                if "thumbnail" not in product.keys():
                    product["thumbnail"] = product["alert"]["graphics"]["src"]
                public_store_items.append(Product(**product))
        public_filtered = self.__filter_items(public_store_items, self.filters)
        for item in public_filtered:
            self.__download_images(item)
        return public_filtered

    def __filter_items(self, items: List[Product], filters: List[str]):
        for filter in filters:
            items = [item for item in items if filter not in item.name]
        return items

    def __remove_all_images(self):
        for item in os.listdir("./"):
            if item.endswith(".jpg"):
                os.remove(item)

    def __download_images(self, product: Product, path: str = "./images"):
        if not os.path.isdir('./images'):
            os.mkdir(path)
        if not path.endswith("/"):
            path += "/"
        if os.path.isfile(f"{path}{product.id}.jpg"):
            os.remove(f"{path}{product.id}.jpg")
        response = requests.get(product.thumbnail)
        if response.status_code == 200:
            with open(f"{path}{product.id}.jpg", 'wb') as f:
                f.write(response.content)
