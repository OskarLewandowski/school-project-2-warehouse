from multiprocessing import Manager


class Warehouse:
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
        response = True
        return response

    @classmethod
    def WYCOFANIE(cls, product_name):
        cls._products[product_name]['quantity'] = -9999999
        response = True
        return response

    @classmethod
    def POJEDYNCZE_ZAOPATRZENIE(cls, product_name):
        current_quantity = cls._products[product_name]['quantity']

        if current_quantity >= 0:
            cls._products[product_name]['quantity'] += 1

            response = True
        else:
            response = False

        return response

    @classmethod
    def POJEDYNCZE_ZAMOWIENIE(cls, product_name):
        available_quantity = cls._products[product_name]['quantity']

        if available_quantity >= 1:
            cls._products[product_name]['quantity'] -= 1
            response = True
        else:
            response = False
        return response

    @classmethod
    def PODAJ_CENE(cls, product_name):
        cls._promo_co_10_wycen += 1

        if cls._promo_co_10_wycen == 10:
            if product_name not in cls._original_prices:
                cls._original_prices[product_name] = cls._products[product_name]['price']

            promo_price = 0
            cls._promo_co_10_wycen = 0
        else:
            promo_price = cls._products[product_name]['price']

        if cls._promo_co_10_wycen == 0 and product_name in cls._original_prices:
            cls._products[product_name]['price'] = cls._original_prices[product_name]
            del cls._original_prices[product_name]

        return promo_price

    @classmethod
    def init_manager(cls):
        manager = Manager()
        cls._promo_co_10_wycen = manager.Value('i', 0)
        cls._original_prices = manager.dict()
        product_template = {"price": 5, "quantity": 100}
        cls._products = manager.dict({key: manager.dict(product_template) for key in cls._products.keys()})


def main():
    Warehouse.init_manager()


if __name__ == '__main__':
    main()
