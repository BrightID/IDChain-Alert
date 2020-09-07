import json
import time
import asyncio
import requests
from pykeybasebot import Bot
import pykeybasebot.types.chat1 as chat1
from config import *

sent = {}
keybaseBot = None
if KEYBASE_BOT_KEY:
    keybaseBot = Bot(username=KEYBASE_BOT_USERNAME, paperkey=KEYBASE_BOT_KEY, handler=None)

def alert(msg):
    if msg in sent and time.time() - sent[msg] < SENT_TIMEOUT:
        return
    print(time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime()), msg)
    sent[msg] = int(time.time())
    if KEYBASE_BOT_KEY:
        channel = chat1.ChatChannel(**KEYBASE_BOT_CHANNEL)
        asyncio.run(keybaseBot.chat.send(channel, msg))
    if TELEGRAM_BOT_KEY:
        payload = json.dumps({"chat_id": TELEGRAM_BOT_CHANNEL, "text": msg})
        headers = {'content-type': "application/json", 'cache-control': "no-cache"}
        url = f'https://api.telegram.org/bot{TELEGRAM_BOT_KEY}/sendMessage'
        r = requests.post(url, data=payload, headers=headers)
        print(r.text)


def check():
    payload = json.dumps({"jsonrpc": "2.0", "method": "clique_status", "params": [], "id": 1})
    headers = {'content-type': "application/json", 'cache-control': "no-cache"}
    r = requests.request("POST", IDCHAIN_RPC_URL, data=payload, headers=headers)
    status = r.json()['result']
    numBlocks = status['numBlocks']
    sealersCount = len(status['sealerActivity'])
    for sealer, sealedBlock in status['sealerActivity'].items():
        if sealedBlock <= max(0, (numBlocks/sealersCount - SEALING_BORDER)):
            alert(f'IDChain node {sealer}  is not sealing blocks!')

if __name__ == '__main__':
    while True:
        try:
            check()
            time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt as e:
            raise
        except Exception as e:
            print(e)
