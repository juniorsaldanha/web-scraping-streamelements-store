# Automation/Web Scraping of StreamElements Store - Python3

This project is just to alerts user from new products in Stream Elements Store.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install libs/requirements. 

```bash

git clone https://github.com/juniorsaldanha/web-scraping-gaules-store
cd web-scraping-gaules-store
pip3 install -f requirements.txt
```
## Rename or Copy telegram_model.json to telegram.json and set tha variables

 ```bash
 cp telegram_model.json telegram.json
 nano telegram.json
 ```

## Usage
If u have done everything rith, just type the following command to start the service. 
```bash
python3 __main__.py -c channelName -i valueInterval
```
Example to collect data from gaules channel on interval of 30 seconds
```bash
python3 __main__.py -c gaules -i 30
```
## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)