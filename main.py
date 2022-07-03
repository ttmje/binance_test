import asyncio
import websockets
import json
import requests
from datetime import datetime

now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S') # метка времени в формате год-месяц-день часы-минуты-секунды

class Client():

    def get_snapshot(self):
        url = "https://api.binance.com/api/v3/depth?symbol=MATICUSDT&limit=10"
        self.r = requests.get(url)
        self.orderbook = json.loads(self.r.content)
        self.LastUpdateID = self.orderbook['lastUpdateId']
        print('LastUpdateID is:', self.LastUpdateID, 'shapshot at: ', now)

    def save_orderbook(self):
       with open(f'OBsnapshot_{now}.txt', "w") as file:
           file.write(self.r.text)

    async def depth(self):
        urlws = "wss://stream.binance.com:9443/stream?streams=maticusdt@depth@100ms"
        async with websockets.connect(urlws) as websocket:
            task.get_snapshot()
            #task.save_orderbook()
            while True:
               data = json.loads(await websocket.recv())['data']
               if data['U'] <=  self.orderbook['lastUpdateId'] + 1 and data['u'] >=  self.orderbook['lastUpdateId'] + 1:
                   self.orderbook['lastUpdateId'] = data['u']
                   self.update_order_book(data)
               else:
                   print('discard update')

    async def bookticker(self):
        urlbt = "wss://stream.binance.com:9443/stream?streams=maticusdt@bookTicker"
        async with websockets.connect(urlbt) as websocket2:
            with open(f'BookTickerDATA_{now}.txt', "a") as file:
                while True:
                    self.data2 = json.loads(await websocket2.recv())['data']
                    print('Book Ticker best bids: ', self.data2['b'], self.data2['B'], "Last update id: ", self.data2['u'])
                    print('Book Ticker best asks: ', self.data2['a'], self.data2['A'], "Last update id: ", self.data2['u'])
                    file.writelines(f"best ask: {self.data2['a']}, best bid: {self.data2['b']}, Last update id: {self.data2['u']} \n")


    def update_order_book(self, data):
        with open(f'OrderBookData_{now}.txt', "a") as file:
            for update in data['b']:
                self.manage_orderbook('bids', update)
            print('Order book best bids: ', self.orderbook['bids'][0],  "Last update id: ", data['u'])
            for update in data['a']:
                self.manage_orderbook('asks', update)
            print('Order book best asks: ', self.orderbook['asks'][0], "Last update id: ", data['u'])
            file.writelines(f"best ask: {self.orderbook['asks'][0]}, best bid: {self.orderbook['bids'][0]}, Last update id: {data['u']} \n")

    def manage_orderbook(self, side, update):
        price, qty = update
        # проходимся по всему ордербуку
        for x in range(0, len(self.orderbook[side])):
            if price == self.orderbook[side][x][0]:
                # если количество 0 - удаляем
                # иначе - делаем апдейт
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

    async def both(self):
        await asyncio.gather(task.bookticker(), task.depth())

if __name__ == '__main__':
    task = Client()
    asyncio.run(task.both())

