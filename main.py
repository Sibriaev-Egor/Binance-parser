import logging
import requests
import json
import concurrent.futures

def settings():
    url = 'https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search'
    myobj = {
        "fiat": "UAH",
        "page": 1,
        "rows": 10,
        "tradeType": "BUY",
        "asset": "USDT",
        "countries": [],
        "proMerchantAds": False,
        "shieldMerchantAds": False,
        "publisherType": None,
        "payTypes": [],
        "classifies": [
            "mass",
            "profession"
        ]
    }
    with open('settings.json') as file:
        mySettings = json.load(file)
        myobj.update(mySettings)

    return url, myobj

def logmaker():
    log_formatter = logging.Formatter('%(asctime)s\n%(message)s\n',
                                      datefmt='%d.%m.%Y %H:%M:%S')

    file_handler = logging.FileHandler(filename="file.txt")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(log_formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(log_formatter)

    app_log = logging.getLogger('root')
    app_log.setLevel(logging.INFO)
    app_log.addHandler(file_handler)
    app_log.addHandler(file_handler)
    app_log.addHandler(stream_handler)

def printAll(asset, response):
    arr = []
    for page in response:
        for res in page:
            info = {
                "price": res["adv"]["price"],
                "tradableQuantity": res["adv"]["tradableQuantity"],
                "maxSingleTransAmount": res["adv"]["maxSingleTransAmount"],
                "minSingleTransAmount": res["adv"]["minSingleTransAmount"],
                "commissionRate": res["adv"]["commissionRate"],

                "userNo": res["advertiser"]["userNo"],
                "nickname": res["advertiser"]["nickName"],
                "positiveRate": res["advertiser"]["positiveRate"],
                "monthOrderCount": res["advertiser"]["monthOrderCount"],
                "monthFinishRate": res["advertiser"]["monthFinishRate"],
            }
            arr.append(info)
    logging.info(json.dumps({"asset": asset, "data": arr}, indent=4))

def requestFunction(url, setJSON, page):
    setJSON = setJSON.copy()
    setJSON["page"] = page

    response = requests.post(url, json=setJSON)
    return response.json()["data"]

def getPages(asset, setJSON, url):
    setJSON = setJSON.copy()
    setJSON["asset"] = asset
    resArray = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        pagesAray = []
        for i in range(5):
            pagesAray.append(executor.submit(requestFunction, url, setJSON, i+1))

        for response in concurrent.futures.as_completed(pagesAray):
            resArray.append(response.result())

    return asset, resArray

def main():
    logmaker()
    url, setJSON = settings()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        assetArray = []
        for i in setJSON["asset"]:
            assetArray.append(executor.submit(getPages, i, setJSON, url))

        for response in concurrent.futures.as_completed(assetArray):
            asset, res = response.result()
            printAll(asset, res)

main()
