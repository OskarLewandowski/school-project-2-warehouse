import json
import multiprocessing
import os
import time
from time import sleep
from typing import List, Optional
from queue import Empty
import typing
from fastapi import FastAPI
from pydantic import BaseModel
import requests
import logging

##########################
##    Model danych
##########################

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Actions(BaseModel):
    id: Optional[int] = None
    typ: Optional[str] = None
    product: Optional[str] = None
    liczba: Optional[int] = None
    grupaProduktów: Optional[typing.Dict[str, int]] = None
    cena: Optional[int] = None


class Replies(BaseModel):
    id: Optional[int] = None
    typ: Optional[str] = None
    product: Optional[str] = None
    liczba: Optional[int] = None
    cena: Optional[int] = None
    grupaProduktów: Optional[typing.Dict[str, int]] = None
    stanMagazynów: Optional[typing.Dict[str, int]] = None
    raportSprzedaży: Optional[typing.Dict[str, int]] = None
    cenaZmieniona: Optional[bool] = None
    zrealizowanePrzywrócenie: Optional[bool] = None
    zrealizowaneZamowienie: Optional[bool] = None
    zrealizowaneWycofanie: Optional[bool] = None
    zebraneZaopatrzenie: Optional[bool] = None
    studentId: Optional[int] = None
    timestamp: Optional[int] = None


class Handshake(BaseModel):
    ip_addr: str
    port: int
    indeks: int


global Product
Product = {
    'BULKA': 0,
    'CHLEB': 1,
    'SER': 2,
    'MASLO': 3,
    'MIESO': 4,
    'SOK': 5,
    'MAKA': 6,
    'JAJKA': 7
}
global n_workers
n_workers = 4

global MyActions
MyActions = ["PODAJ_CENE", "POJEDYNCZE_ZAMOWIENIE", "POJEDYNCZE_ZAOPATRZENIE", "WYCOFANIE", "PRZYWROCENIE",
             "ZAMKNIJ_SKLEP"]

## Uruchomienie clienta
app = FastAPI()

## Ustawienie adresów i portów serwera i klienta
SERVER_IP = 'localhost'
SERVER_PORT = 8080

CLIENT_IP = 'localhost'
CLIENT_PORT = 8889

INDEKS = 448700


## Funkcja do przetwarzania danych, otrzymuje na wejściu kolejkę akcji do wykonania
def function(queue: multiprocessing.Queue):
    lock = multiprocessing.Lock()
    barrier = multiprocessing.Barrier(n_workers, timeout=2)
    manager = multiprocessing.Manager()
    response_queue = manager.list()

    promo_co_10_wycen = multiprocessing.Value('i', 0)
    price = multiprocessing.Array('i', [5] * 8)
    quantity = multiprocessing.Array('i', [100] * 8)
    id_queue_list = manager.list()

    workers = [
        multiprocessing.Process(target=process, args=(
            queue, response_queue, price, quantity, promo_co_10_wycen, lock, barrier, id_queue_list))
        for _ in range(n_workers)]

    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join()

    print("\nIlość procesów:", n_workers)
    print(f"Wynik: {len(response_queue)}")

    # Odesłanie listy wyników do serwera
    url = f"http://{SERVER_IP}:{SERVER_PORT}/action/replies"
    data = json.dumps([obj.__dict__ for obj in response_queue])
    headers = {'Content-type': 'application/json'}
    sleep(1)
    r = requests.post(url, data=data, headers=headers)
    logging.info(r)
    r.close()


## Metoda dla wątków do procesowania. Tylko przykład, można tworzyć różne metody dla różnych wątków, wszystkie opcje są
## dozwolone
def process(queue, response_queue, price, quantity, promo_co_10_wycen, lock, barrier, id_queue_list):
    while True:
        try:
            data = queue.get(timeout=0.007)

            if data.typ in MyActions:

                try:
                    with lock:
                        id_queue_list.append(data.id)

                    barrier.wait()
                except:
                    barrier.abort()

                while True:
                    with lock:
                        if data.id == min(id_queue_list):
                            id_queue_list.remove(data.id)
                            break
                    time.sleep(0.00777)

                if data.typ == "PODAJ_CENE":
                    answer = Replies()
                    answer.id = data.id
                    answer.typ = data.typ
                    answer.product = data.product
                    answer.studentId = INDEKS

                    with lock:
                        promo_co_10_wycen.value += 1

                        if promo_co_10_wycen.value == 10:
                            promo_co_10_wycen.value = 0
                            answer.cena = 0  # Value PROMO_CO_10_WYCEN
                        else:
                            answer.cena = 5

                        print(id_queue_list)
                        print(answer)
                        response_queue.append(answer)

                elif data.typ == "POJEDYNCZE_ZAMOWIENIE":
                    answer = Replies()
                    answer.id = data.id
                    answer.typ = data.typ
                    answer.product = data.product
                    answer.liczba = 1
                    answer.studentId = INDEKS
                    with (lock):
                        if quantity[Product.get(data.product)] >= 1:
                            quantity[Product.get(data.product)] -= 1
                            answer.zrealizowaneZamowienie = True
                        else:
                            answer.zrealizowaneZamowienie = False

                        print(id_queue_list)
                        print(answer)
                        response_queue.append(answer)

                elif data.typ == "POJEDYNCZE_ZAOPATRZENIE":
                    answer = Replies()
                    answer.id = data.id
                    answer.typ = data.typ
                    answer.product = data.product
                    answer.liczba = 1
                    answer.studentId = INDEKS
                    with lock:
                        if quantity[Product.get(data.product)] >= 0:
                            quantity[Product.get(data.product)] += 1
                            answer.zebraneZaopatrzenie = True
                        else:
                            answer.zebraneZaopatrzenie = False

                        print(id_queue_list)
                        print(answer)
                        response_queue.append(answer)

                elif data.typ == "WYCOFANIE":
                    answer = Replies()
                    answer.id = data.id
                    answer.typ = data.typ
                    answer.product = data.product
                    answer.studentId = INDEKS
                    with lock:
                        quantity[Product.get(data.product)] = -9999999
                        answer.zrealizowaneWycofanie = True

                        print(id_queue_list)
                        print(answer)
                        response_queue.append(answer)

                elif data.typ == "PRZYWROCENIE":
                    answer = Replies()
                    answer.id = data.id
                    answer.typ = data.typ
                    answer.product = data.product
                    answer.studentId = INDEKS
                    with lock:
                        quantity[Product.get(data.product)] = 0
                        answer.zrealizowanePrzywrócenie = True

                        print(id_queue_list)
                        print(answer)
                        response_queue.append(answer)

                elif data.typ == "ZAMKNIJ_SKLEP":
                    answer = Replies()
                    answer.id = data.id
                    answer.typ = data.typ
                    answer.product = data.product
                    answer.studentId = INDEKS
                    with lock:
                        inventory = {product: quantity[Product[product]] for product in Product}
                        prices = {product: price[Product[product]] for product in Product}

                        answer.stanMagazynów = inventory
                        answer.grupaProduktów = prices

                        print(id_queue_list)
                        print(answer)
                        response_queue.append(answer)

        except Empty:
            print("Kolejka jest pusta, kończenie pracy procesu...")
            break
        except Exception as e:
            print("Błąd:", e)


## Odbiera listę operacji od serwera
@app.post("/push-data", status_code=201)
async def create_sensor_data(actions: List[Actions]):
    queue = multiprocessing.Queue()

    for action in actions:
        queue.put(action)

    logging.info('Processing')

    process_worker = multiprocessing.Process(target=function, args=(queue,))
    process_worker.start()
    process_worker.join()


## Laczy się z serwerem i przesyła mu swój numer IP i port
@app.get("/hello")
async def say_hello():
    url = f"http://{SERVER_IP}:{SERVER_PORT}/action/handshake"
    medata = {
        "port": CLIENT_PORT,
        "ip_addr": CLIENT_IP,
        "indeks": INDEKS
    }
    me = Handshake(**medata)
    data = json.dumps(medata)
    headers = {'Content-type': 'application/json'}
    res = requests.post(url, data=data, headers=headers)
    if (res.status_code == 201 or res.status_code == 200):
        return ("Success")
    else:
        return (f"Error occurred {res.text}")
