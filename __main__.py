from selenium import webdriver
from time import sleep
from datetime import datetime
import json, requests, os

class start():
    def __init__(self,CHANNEL:str,PATH:str):
        self.URL = f'https://streamelements.com/{CHANNEL}/store'
        self.PATH = PATH + '/chromedriver'
        self.OPTIONS = webdriver.ChromeOptions()
        self.OPTIONS.add_argument("--no-sandbox") 
        self.OPTIONS.add_argument("--disable-setuid-sandbox") 
        self.OPTIONS.add_argument("--remote-debugging-port=9222")
        self.OPTIONS.add_argument("--disable-dev-shm-using") 
        self.OPTIONS.add_argument("--disable-extensions") 
        self.OPTIONS.add_argument("--disable-gpu") 
        self.OPTIONS.add_argument("start-maximized") 
        self.OPTIONS.add_argument("disable-infobars") 
        self.OPTIONS.add_argument('headless')
        self.driver = webdriver.Chrome(self.PATH, options=self.OPTIONS)
        self.dado_top = list()
        self.telegram = telegram(PATH=PATH)
        self.firstTime = True
    def abre_a_page(self,):
        self.page = self.driver.get(self.URL)
        sleep(3)
        self.dado_bruto = self.driver.find_elements_by_xpath('//*[@id="app"]/div/md-content/div[1]/div[2]/div[3]')[0].text.split('\n')

    def atualiza_a_page(self,):
        self.driver.refresh()
        sleep(3)
        self.dado_bruto = self.driver.find_elements_by_xpath('//*[@id="app"]/div/md-content/div[1]/div[2]/div[3]')[0].text.split('\n')
    
    def parse_a_page(self,):
        self.dado_anterior = self.dado_top
        self.dado_top = []
        for var,ind in zip(self.dado_bruto,range(0,len(self.dado_bruto))):
            if var == 'description':
                item = {}
                item['Product'] = self.dado_bruto[ind-1]
                item[var] = self.dado_bruto[ind+1]
                item['Left'] = self.dado_bruto[ind+3].split(' ')[0]
                if item['Left'] == 'Sold': item['Left'] = 0 
                item['Cost'] = self.dado_bruto[ind+5].split(' ')[0]
                self.dado_top.append(item)

    def sleep(self,x): sleep(x-3)

    def mostra_os_itens(self,):
        for item in self.dado_top: print(item)
        print(f'{datetime.now()}\n')
        
    def fecha_o_trem_ai(self,):
        self.driver.close()
    
    def pegar_novos_itens(self,):
        self.newItens = []
        for item in self.dado_top:
            if item not in self.dado_anterior and item['Left'] != 0:
                self.newItens.append(item)
        if len(self.newItens) > 0 and self.firstTime != True:
            print(f"{len(self.newItens)} novos itens!\n")
            self.send_tl()
            return self.newItens
        self.firstTime = False
        print(f"{len(self.newItens)} itens! NENHUM ITEM NOVO")
        return []
    
    def send_tl(self,):
        for item in self.newItens:
            if item is dict:
                item = str(item)
            self.telegram.send(f"""
                ITEM DISPONIVEL:
                Procuct: {item['Product']}
                Left: {item['Left']}
                Cost: {item['Cost']}
            """)

class telegram():
    def __init__(self,PATH:str):
        self.telegramConf = json.load(open(PATH+'/telegram.json'))
        self.bot_token = self.telegramConf['telegram']['token']
        self.chat_id = self.telegramConf['telegram']['chat_id']
        
    def send(self, bot_message):
        send_text = 'https://api.telegram.org/bot' + self.bot_token + '/sendMessage?chat_id=' + self.chat_id + '&parse_mode=Markdown&text=' + bot_message
        response = requests.get(send_text)
        return response.json()['ok']

if __name__ == "__main__":
    PATH = os.path.dirname(os.path.realpath(__file__))
    conf = json.load(open(PATH+'/telegram.json'))
    x = start(conf['env']['STREAMELEMENTS_CHANNEL'], PATH)
    x.abre_a_page()
    while True:
        x.atualiza_a_page()
        x.parse_a_page()
        x.pegar_novos_itens()
        x.sleep(conf['env']['Interval'])