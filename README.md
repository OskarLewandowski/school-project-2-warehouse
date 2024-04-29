Problem: Napisz program przetwarzający zadania symulujące pracę magazynu.

Serwer losowo wybiera akcje które są przekazywane do wykonania, akcje dzielą się na 4 sekcje wycena (akcje związane z cenami produktów), zamówienia (akcje związane z zakupami produktów), zaopatrzenie (akcje związane z dostarczeniem produktów do magazynu), wydarzenia (akcje specjalne jak inwentaryzacja).

Akcje
Klienci wykonują akcje na magazynie, lista dostępnych akcji:

PODAJ_CENE, ZMIEN_CENE

POJEDYNCZE_ZAMOWIENIE, GRUPOWE_ZAMOWIENIE, REZERWACJA, ODBIÓR_REZERWACJI

POJEDYNCZE_ZAOPATRZENIE, GRUPOWE_ZAOPATRZENIE

WYCOFANIE, PRZYWROCENIE, INWENTARYZACJA, RAPORT_SPRZEDAŻY

Dodatkowo dzielimy akcje na scenariusze, według których goraniczamy akcje które procesujemy, np scenariusz cena bez zmian nie będzie odpowiadać na akcje zmiana ceny itd. Każdy student otrzymuje losowe 4 scenariusze, które ma spełnić z zakresu scenariuszy dostępnych w systemie, scenariusze:

Wycena


CENA_BEZ_ZMIAN - program odpowiada na zapytania o cenę, ale ona jest zawsze niezmienna.
CENA_ZMIENNA - program odpowiada na zapytania o cenę oraz ceny mogą zmieniać się w czasie działania magazynu.
PROMO_CO_10_WYCEN - program odpowiada na zapytania o cenę, które się nie zmieniają, ale co 10 przychodzące zapytanie traktowane jest jako promocja i wyceniane jest na 0.
Zamówienie


POJEDYNCZE - program przyjmuje zamówienia na pojedyncze produkty, zamówienia zawsze są na 1 sztukę
GRUPOWE - program przyjmuje zamówienia na pojedyncze sztuki jak i na grupy produktów (grupa może składać się tylko z 1 produktu), zamówienia zawsze są na 1 sztukę każdego produktu
REZERWACJA - program przyjmuje rezerwacje, które są pobierane ze stanów magazynowych i odbierane przez akcje odbiór zamówienia
Zaopatrzenie


POJEDYNCZE - program przyjmuje do magazynu zaopatrzenie z pojedynczymi produktami, zaopatrzenie dodaje zawsze 1 sztukę
GRUPOWE - program przyjmuje do magazynu zaopatrzenie z pojedynczymi produktami jak i z grupami produktów, zaopatrzenie dodaje zawsze 1 sztukę kazdego produktu
Wydarzenie


WYCOFANIE - program obsługuje wycofanie produktu ze sprzedaży, które ustala stan magazynowy na -9999999L oraz przywrócenie produktu które zeruje stan magazynu, gdy produkt jest wycofany ze sprzedaży nie obsługujemy jego zaopatrzenia (zamowenia nie są realizowane)
INWENTARYZACJA - program obsługuje zapytania o inwentaryzację, które musi wypisać stan magazynu na dokładny moment wystąpienia inwentaryzacji
RAPORT_SPRZEDAŻY - program obsługuje zapytania o raport sprzedaży, na które musi odpowiedzieć raportem ze sprzedaży (produkt, liczba sprzedanych sztuk) na dokładny moment wystąpienia prośby o raport

Każde z scenariuszy obsługuje tylko wybrane typy akcji przychodzących na kolejkę zdarzeń (a resztę pomija!), odpowiednio:

CENY_BEZ_ZMIAN(PODAJ_CENE),
CENA_ZMIENNA(PODAJ_CENE, ZMIEN_CENE),
PROMO_CO_10_WYCEN(PODAJ_CENE);
WYCOFANIE(WYCOFANIE, PRZYWROCENIE),
INWENTARYZACJA(INWENTARYZACJA),
RAPORT_SPRZEDAŻY(RAPORT_SPRZEDAŻY);
POJEDYNCZE (POJEDYNCZE_ZAMOWIENIE),
GRUPOWE (POJEDYNCZE_ZAMOWIENIE, GRUPOWE_ZAMOWIENIE),
REZERWACJE (POJEDYNCZE_ZAMOWIENIE, REZERWACJA, ODBIÓR_REZERWACJI);
POJEDYNCZE (POJEDYNCZE_ZAOPATRZENIE),
GRUPOWE (POJEDYNCZE_ZAOPATRZENIE, GRUPOWE_ZAOPATRZENIE);
Kryteria działania:
Program powinien działać wielowątkowo.
Liczba zrealizowanych oraz niezrealizowanych zamówień (gdy nie ma dostatecznej liczby produktów, produkt jest wycofany itp) musi być taka sama jak przy uruchomieniu jednowątkowym - co znaczy, że odebranie zamówienia musi poczekać na wykonanie wszystkich zamówień, lub w inny sposób należy kontrolować ich odbieranie.
Stan magazynu na koniec musi być taki jak w przypadku działania sekwencyjnego
Ceny produktów na koniec muszą być takie jak w przypadku działania sekwencyjnego
Odpowiedzi odnośnie cen produktów muszą być takie same jak w przypadku działania sekwencyjnego. Uwaga! Kolejność tych odpowiedzi nie ma znaczenia! Ma znaczenie jednak czy pytanie o cenę wystąpiło po zmianie ceny oraz akcja z którym id była promocyjnym zapytaniem.
Odpowiedzi odnośnie inwentaryzacji muszą być takie same jak w przypadku działania sekwencyjnego. Inwentaryzacja musi odbywać się w tym samym czasie, jak w przypadku działania sekwencyjnego - innymi słowy nie powinniśmy obsługiwać zdarzeń zmieniających magazyn przychodzących po niej, zanim jej nie przeprowadzimy, jednocześnie musimy zaczekać na wykonanie zadań zmieniających stan magazynu zanim przeprocesujemy ją samą.
Odpowiedzi odnośnie raportu sprzedaży muszą być takie same jak w przypadku działania sekwencyjnego. Działa podobnie jak inwentaryzacja, tylko dotyczy samych zamówień.
