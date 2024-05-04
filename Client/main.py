import json
import multiprocessing
import threading
from time import sleep
from typing import List, Optional
from queue import Queue, Empty
import typing
from fastapi import FastAPI
from pydantic import BaseModel
import requests
import logging
from warehouse_model import Warehouse


##########################
##    Model danych
##########################

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


## Uruchomienie clienta
app = FastAPI()

## Ustawienie adresów i portów serwera i klienta
SERVER_IP = 'localhost'
SERVER_PORT = 8080

CLIENT_IP = 'localhost'
CLIENT_PORT = 8889

INDEKS = 448700

response_queue = multiprocessing.Queue()


## Funkcja do przetwarzania danych, otrzymuje na wejściu kolejkę akcji do wykonania
def function(queue: multiprocessing.Queue, response_queue: multiprocessing.Queue):
    lock = multiprocessing.Lock()
    manager = multiprocessing.Manager()

    promo_co_10_wycen = multiprocessing.Value('i', 0)

    products = manager.dict({
        key: manager.dict({"price": 5, "quantity": 100})
        for key in ["BULKA", "CHLEB", "SER", "MASLO", "MIESO", "SOK", "MAKA", "JAJKA"]
    })

    n_workers = 4

    workers = [multiprocessing.Process(target=process, args=(queue, response_queue, products, promo_co_10_wycen, lock))
               for _ in range(n_workers)]

    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join()

    # Przykład odpowiedzi dla pojedynczej akcji
    # Lista odpowiedzi
    wynik = []

    while not response_queue.empty():
        wynik.append(response_queue.get())

    print(len(wynik))

    # Odesłanie listy wyników do serwera
    url = f"http://{SERVER_IP}:{SERVER_PORT}/action/replies"
    data = json.dumps([obj.__dict__ for obj in wynik])
    headers = {'Content-type': 'application/json'}
    sleep(1)
    r = requests.post(url, data=data, headers=headers)
    logging.info(r)
    r.close()


## Metoda dla wątków do procesowania. Tylko przykład, można tworzyć różne metody dla różnych wątków, wszystkie opcje są
## dozwolone
def process(queue: multiprocessing.Queue, response_queue: multiprocessing.Queue, lock: multiprocessing.Lock, products,
            promo_co_10_wycen):
    while True:
        try:
            data = queue.get(timeout=0.7)

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
                        answer.cena = 0
                    else:
                        answer.cena = 5

                    print(answer)
                    response_queue.put(answer)

            elif data.typ == "POJEDYNCZE_ZAMOWIENIE":
                answer = Replies()
                answer.id = data.id
                answer.typ = data.typ
                answer.product = data.product
                answer.liczba = 1
                answer.studentId = INDEKS
                with lock:
                    if products[data.product]['quantity'] >= 1:
                        products[data.product]['quantity'] -= 1
                        answer.zebraneZaopatrzenie = True
                    else:
                        answer.zebraneZaopatrzenie = False

                    print(answer)
                    response_queue.put(answer)

            elif data.typ == "POJEDYNCZE_ZAOPATRZENIE":
                answer = Replies()
                answer.id = data.id
                answer.typ = data.typ
                answer.product = data.product
                answer.liczba = 1
                answer.studentId = INDEKS
                with lock:
                    if products[data.product]['quantity'] >= 0:
                        products[data.product]['quantity'] += 1
                        answer.zebraneZaopatrzenie = True
                    else:
                        answer.zebraneZaopatrzenie = False

                    print(answer)
                    response_queue.put(answer)

            elif data.typ == "WYCOFANIE":
                answer = Replies()
                answer.id = data.id
                answer.typ = data.typ
                answer.product = data.product
                answer.studentId = INDEKS
                with lock:
                    products[data.product]['quantity'] = -9999999
                    answer.zrealizowaneWycofanie = True

                    print(answer)
                    response_queue.put(answer)

            elif data.typ == "PRZYWROCENIE":
                answer = Replies()
                answer.id = data.id
                answer.typ = data.typ
                answer.product = data.product
                answer.studentId = INDEKS
                with lock:
                    products[data.product]['quantity'] = 0
                    answer.zrealizowanePrzywrócenie = True

                    print(answer)
                    response_queue.put(answer)

            elif data.typ == "ZAMKNIJ_SKLEP":
                answer = Replies()
                answer.id = data.id
                answer.typ = data.typ
                answer.product = data.product
                answer.studentId = INDEKS
                with lock:
                    inventory = {product: details['quantity'] for product, details in products.items()}
                    prices = {product: details['price'] for product, details in products.items()}
                    answer.stanMagazynów = inventory
                    answer.grupaProduktów = prices

                    print(answer)
                    response_queue.put(answer)

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

    process_worker = multiprocessing.Process(target=function, args=(queue, response_queue))
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
