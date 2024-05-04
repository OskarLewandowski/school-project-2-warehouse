class Warehouse:
    _promo_co_10_wycen = 0

    _products = {
        "BULKA": {"price": 5, "quantity": 100},
        "CHLEB": {"price": 5, "quantity": 100},
        "SER": {"price": 5, "quantity": 100},
        "MASLO": {"price": 5, "quantity": 100},
        "MIESO": {"price": 5, "quantity": 100},
        "SOK": {"price": 5, "quantity": 100},
        "MAKA": {"price": 5, "quantity": 100},
        "JAJKA": {"price": 5, "quantity": 100}
    }

    @classmethod
    def ZAMKNIJ_SKLEP(cls):
        final_inventory = {product: details['quantity'] for product, details in cls._products.items()}
        final_prices = {product: details['price'] for product, details in cls._products.items()}

        # restore warehouse
        for product in cls._products.keys():
            cls._products[product]['price'] = 5
            cls._products[product]['quantity'] = 100

        return final_inventory, final_prices

    @classmethod
    def PRZYWROCENIE(cls, product_name):
        cls._products[product_name]['quantity'] = 0
        return True

    @classmethod
    def WYCOFANIE(cls, product_name):
        cls._products[product_name]['quantity'] = -9999999
        return True

    @classmethod
    def POJEDYNCZE_ZAOPATRZENIE(cls, product_name):
        if cls._products[product_name]['quantity'] >= 0:
            cls._products[product_name]['quantity'] += 1
            return True
        else:
            return False

    @classmethod
    def POJEDYNCZE_ZAMOWIENIE(cls, product_name):
        if cls._products[product_name]['quantity'] >= 1:
            cls._products[product_name]['quantity'] -= 1
            return True
        else:
            return False

    @classmethod
    def PODAJ_CENE(cls, product_name):
        cls._promo_co_10_wycen += 1

        if cls._promo_co_10_wycen == 10:
            cls._promo_co_10_wycen = 0
            return 0

        return cls._products[product_name]['price']
