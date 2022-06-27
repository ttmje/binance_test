import asyncio
import websockets
import json
import requests
from datetime import datetime

now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

def http():
    url = "https://api.binance.com/api/v3/depth?symbol=MATICUSDT&limit=1000"
    r = requests.get(url)
    print(f'ORDER BOOK SNAPSHOT AT {now}: ', r.text)
    f = open(f'OBsnapshot_{now}.txt', "w")
    f.write(r.text)

async def ws():

    urlws = "wss://stream.binance.com:9443/stream?streams=maticusdt@depth@100ms"
    async with websockets.connect(urlws) as websocket:
        while True:
           data = json.loads(await websocket.recv())['data']
           print(data)

if __name__ == '__main__':
   http()
   loop = asyncio.get_event_loop()
   loop.run_until_complete(ws())
