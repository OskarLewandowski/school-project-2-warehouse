from multiprocessing import Lock


class Warehouse:
    _lock = Lock()

    _promo_co_10_wycen = 0
    _original_prices = {}

    _products = {
        "BULKA": {"price": 5, "quantity": 100},
        "CHLEB": {"price": 5, "quantity": 100},
        "SER": {"price": 5, "quantity": 100},
        "MASLO": {"price": 5, "quantity": 100},
        "MIESO": {"price": 5, "quantity": 100},
        "SOK": {"price": 5, "quantity": 100},
        "MAKA": {"price": 5, "quantity": 100},
        "JAJKO": {"price": 5, "quantity": 100}
    }

    _sales = {key: 0 for key in _products}

    @classmethod
    def POJEDYNCZE_ZAMOWIENIE(cls, product_name):
        with cls._lock:
            if product_name in cls._products:
                available_quantity = cls._products[product_name]['quantity']
                if available_quantity >= 1:
                    cls._products[product_name]['quantity'] -= 1
                    cls._sales[product_name] += 1
                    response = {"product": product_name, "ordered_quantity": 1, "order_fulfilled": True}
                else:
                    response = {"product": product_name, "ordered_quantity": 1, "order_fulfilled": False}
                return response

    @classmethod
    def PODAJ_CENE(cls, product_name):
        with cls._lock:
            if product_name in cls._products:
                cls._promo_co_10_wycen += 1

                if cls._promo_co_10_wycen == 10:
                    if product_name not in cls._original_prices:
                        cls._original_prices[product_name] = cls._products[product_name]['price']

                    promo_price = 0
                    print(f"Cena promocyjna dla {product_name}: {promo_price} zł")

                    cls._promo_co_10_wycen = 0
                else:
                    promo_price = cls._products[product_name]['price']
                    print(f"Cena dla {product_name}: {promo_price} zł")

                if cls._promo_co_10_wycen == 0 and product_name in cls._original_prices:
                    cls._products[product_name]['price'] = cls._original_prices[product_name]
                    del cls._original_prices[product_name]

                return {"product": product_name, "price": promo_price}

    @classmethod
    def update(cls, name, price=None, quantity=None):
        with cls._lock:
            if name in cls._products:
                if price is not None:
                    cls._products[name]["price"] = price
                if quantity is not None:
                    cls._products[name]["quantity"] = quantity

    @classmethod
    def info(cls, name):
        with cls._lock:
            if name in cls._products:
                return cls._products[name].copy()

    @classmethod
    def summary(cls):
        with cls._lock:
            for product, details in cls._products.items():
                print(f"Nazwa - {product}, Cena - {details['price']}, Ilość - {details['quantity']}")

    @classmethod
    def display_sales(cls):
        with cls._lock:
            print("Rejestr sprzedaży:")
            for product, sold_quantity in cls._sales.items():
                print(f"{product}: Sprzedano {sold_quantity} sztuk")


# Testowanie
warehouse = Warehouse
for i in range(15):
    warehouse.PODAJ_CENE("CHLEB")
    warehouse.PODAJ_CENE("JAJKO")
    warehouse.POJEDYNCZE_ZAMOWIENIE("CHLEB")

warehouse.summary()
warehouse.POJEDYNCZE_ZAMOWIENIE("JAJKO")
warehouse.display_sales()

warehouse.POJEDYNCZE_ZAMOWIENIE("CHLEB")
warehouse.display_sales()
warehouse.summary()
