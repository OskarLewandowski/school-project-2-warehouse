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


## Funkcja do przetwarzania danych, otrzymuje na wejściu kolejkę akcji do wykonania
def function(queue: Queue):
    n_workers = 4

    workers = [multiprocessing.Process(target=process, args=(queue,))
               for _ in range(n_workers)]

    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join()

    # Przykład odpowiedzi dla pojedynczej akcji
    odp = Replies()
    odp.studentId = INDEKS
    odp.id = 0
    odp.typ = "PODAJ_CENE"
    odp.cena = 5
    odp.product = "CHLEB"

    odp2 = Replies()
    odp2.studentId = INDEKS
    odp2.id = 0
    odp2.product = "CHLEB"
    odp2.liczba = 1
    odp2.zrealizowaneZamowienie = True
    odp2.typ = "POJEDYNCZE_ZAMOWIENIE"

    odp3 = Replies()
    odp3.id = 1
    odp3.studentId = INDEKS
    odp3.typ = "ZAMKNIJ_SKLEP"
    odp3.stanMagazynów = {}
    odp3.grupaProduktów = {}

    # Lista odpowiedzi
    wynik = [odp, odp2, odp3]

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
def process(queue: Queue):
    while True:
        try:
            data = queue.get(timeout=0.5)
            print(data)
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
