from bs4 import BeautifulSoup
from requests_html import HTMLSession
from time import sleep
import json, os, argparse, requests, sys

#Args
parser = argparse.ArgumentParser()
parser.add_argument("--channel", "-c", help="Channel name  that you want to monitor the store! default:gaules", default='gaules',type=str)
parser.add_argument("--interval", "-i", help="Interval of check time (in seconds, integer)! default: 30", default=30, type=int)
parser.add_argument("--type", "-t", help="Category/Type of item to alert in Telegram! default:skins, available: skins, ak47, m4a4, knife, awp, all", default='skins',type=str)
args = parser.parse_args()

class telegram():
    def __init__(self,):
        try:
            self.telegramConf = json.load(open(os.path.dirname(os.path.abspath(__file__))+'/telegram.json'))
        except:
            print(f"U need to create telegram.json with bot info and chat id! copy model from telegram_model.json")
            sys.exit(1)
        self.bot_token = self.telegramConf['telegram']['token']
        self.chat_id = self.telegramConf['telegram']['chat_id']

    def send(self, bot_message):
        send_text = f'https://api.telegram.org/bot{self.bot_token}/sendMessage?chat_id={self.chat_id}&parse_mode=Markdown&text={bot_message}'
        response = requests.get(send_text)
        return response.json()['ok']

class scrapping():
    def __init__(self, channel:str):
        self.TELEGRAM = telegram()
        self.CHANNEL = channel
        self.URL = f'https://streamelements.com/{self.CHANNEL}/store'
        self.SKINS = []

    def GetHTMLSession(self, url:str):
        return HTMLSession().get(url)

    def GetHTMLRended(self, url:str, timeout:int = 60):
        var = self.GetHTMLSession(url)
        var.html.render(timeout=timeout)
        var = BeautifulSoup(var.html.html,'html.parser')
        return var

    def GetListOfProducts(self,):
        PAGE = self.GetHTMLRended(self.URL)
        PRODUCTS_LIST = []
        PRODUCTS_LIST_DICT = []
        for product in PAGE.find_all('md-card-content')[1:]:
            PRODUCTS_LIST.append(list(product.stripped_strings))
        for product in PRODUCTS_LIST:
            productDict = {}
            for var,index in zip(product,range(len(product))):
                if index == 0: productDict['product'] = var
                if 'description' in var:
                    productDict['description'] = product[index+1]
                if 'shopping_basket' in var:
                    if product[index+1] != 'Sold out': productDict['quantity'] = int(product[index+1].split(' ')[0])
                    else: productDict['quantity'] = 0
                if 'monetization_on' in var:
                    productDict['cost'] = int(product[index+1])
            PRODUCTS_LIST_DICT.append(productDict)
        # print(*PRODUCTS_LIST_DICT, sep='\n\n')
        # sleep(1)
        if len(PRODUCTS_LIST_DICT) == 0: self.GetListOfProducts()
        else: self.PRODUCS_LIST_DICT = PRODUCTS_LIST_DICT

    def SepareProductsInGroups(self,):
        SKINS, KNIFES, AK47, M4A4, AWP, = [], [], [], [], []
        for product in self.PRODUCS_LIST_DICT:
            if 'Estado' in product['description']: SKINS.append(product)
            if 'Knife' in product['product']: KNIFES.append(product)
            if 'M4A4' in product['product']: M4A4.append(product)
            if 'AK-47' in product['product']: AK47.append(product)
            if 'AWP' in product['product']: AWP.append(product)
        self.SKINS   = SKINS
        self.KNIFES  = KNIFES
        self.AK47    = AK47
        self.M4A4    = M4A4
        self.AWP     = AWP

    def SendTLOfProductsAvailable(self, data:list = None):
        if data is None: data = self.SKINS
        status = bool
        for product in data:
            if product['quantity'] > 0:
                status = self.TELEGRAM.send(
f"""ITEM DISPONIVEL:
Product: {product['product']}
Quantity: {product['quantity']}
Cost: {product['cost']}""")
                if not status: print("MSG Não enviada!")
        if status: print(f"{len(data)} itens enviados!")

if __name__ == "__main__":
    scrap = scrapping(args.channel)
    while True:
        print(f"\nRunning in CHANNEL: {args.channel}, alerting {args.type}, with INTERVAL: {args.interval} seconds")
        try:
            scrap.GetListOfProducts()
            scrap.SepareProductsInGroups()
            if args.type == 'skins': scrap.SendTLOfProductsAvailable()
            elif args.type == 'ak47': scrap.SendTLOfProductsAvailable(scrap.AK47)
            elif args.type == 'ma4a': scrap.SendTLOfProductsAvailable(scrap.M4A4)
            elif args.type == 'knifes': scrap.SendTLOfProductsAvailable(scrap.KNIFES)
            elif args.type == 'awp': scrap.SendTLOfProductsAvailable(scrap.AWP)
            elif args.type == 'all': scrap.SendTLOfProductsAvailable(scrap.PRODUCS_LIST_DICT)
            else:
                print(f"ERROR: Type invalid: {args.type} doesnt exist!, use one of [skins, ak47, m4a4, knife, awp, all]!")
                sys.exit(1)
        except Exception as err:
            print(f"ERROR: {err}\n")
            pass
        sleep(args.interval)
