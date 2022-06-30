import asyncio
import websockets
import json
import requests
from datetime import datetime

now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

class Client():

    def get_snapshot(self):
        url = "https://api.binance.com/api/v3/depth?symbol=FIROUSDT&limit=10"
        self.r = requests.get(url)
        self.orderbook = json.loads(self.r.content)
        self.LastUpdateID = self.orderbook['lastUpdateId']
        print('LastUpdateID is:', self.LastUpdateID, 'shapshot at: ', now)

    def save_orderbook(self):
       with open(f'OBsnapshot_{now}.txt', "w") as file:
           file.write(self.r.text)

    async def depth(self):
        urlws = "wss://stream.binance.com:9443/stream?streams=firousdt@depth@1000ms"
        async with websockets.connect(urlws) as websocket:
            task.get_snapshot()
            task.save_orderbook()
            while True:
               data = json.loads(await websocket.recv())['data']
               if data['U'] <=  self.orderbook['lastUpdateId'] + 1 and data['u'] >=  self.orderbook['lastUpdateId'] + 1:
                   self.orderbook['lastUpdateId'] = data['u']
                   self.update_order_book(data)
                   #print(self.data)
               else:
                   print('discard update')

    def update_order_book(self, data):
        for update in data['b']:
            self.manage_orderbook('bids', update)
        print('Best bids: ', self.orderbook['bids'][0])
        for update in data['a']:
            self.manage_orderbook('asks', update)
        print('Best asks: ', self.orderbook['asks'][0])
        #print('Spread: ')


    def manage_orderbook(self, side, update):
        price, qty = update
        # loop through orderbook side
        for x in range(0, len(self.orderbook[side])):
            if price == self.orderbook[side][x][0]:
                # when qty is 0 remove from orderbook, else
                # update values
                if float(qty) == 0:
                    self.orderbook[side].pop(x)
                    #print(f'Removed {price} {qty}')
                    return
                else:
                    self.orderbook[side][x] = update
                    #print(f'Updated: {price} {qty}')
                    return
        if float(qty) != 0:
            self.orderbook[side].insert(-1, update)
            if side == 'asks':
                self.orderbook[side] = sorted(self.orderbook[side], key=lambda m: float(m[0]))
            else:
                self.orderbook[side] = sorted(self.orderbook[side], key=lambda m: float(m[0]), reverse=True)

if __name__ == '__main__':
    task = Client()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(task.depth())
