import json

class Configuration(object):
    def __init__(self) -> None:
        super().__init__()
        self.__read_file()
    
    def __read_file(self,):
        with open("./appsettings.json","r") as _f:
            self.App = json.load(_f)