import csv
import matplotlib.pyplot as plt
import random


def linearna_funkcija(k, y0, x):
    # Izracunaj y linearne funkcije
    return k * x + y0


def narisi(genders, visine, teze, y0, k, napake, y0_naj, k_naj):
    x1 = 0
    x2 = 100
    y1 = linearna_funkcija(k, y0, x1)
    y2 = linearna_funkcija(k, y0, x2)
    y_naj_1 = linearna_funkcija(k_naj, y0_naj, x1)
    y_naj_2 = linearna_funkcija(k_naj, y0_naj, x2)

    plt.subplot(211)
    # plt.xlim(0, 2)
    # plt.ylim(0, 2)

    # Nariseva tocke moski
    plt.plot([visine[i] for i in range(len(visine)) if genders[i]=='Male'], [teze[i] for i in range(len(visine)) if genders[i]=='Male'], 'o')
    # Nariseva tocke zenski
    plt.plot([visine[i] for i in range(len(visine)) if genders[i]=='Female'], [teze[i] for i in range(len(visine)) if genders[i]=='Female'], 'x')

    # Nariseva trenutno premico
    plt.plot([x1, x2], [y1, y2])
    # Nariseva najboljso premico
    plt.plot([x1, x2], [y_naj_1, y_naj_2])

    plt.subplot(212)

    # Narisem napake
    plt.plot(napake, '-')

    # Da se program ne blokira
    plt.show(block=False)

    # Pocakam malo
    plt.pause(0.0001)

    # Pocisti ko koncas
    plt.clf()



def izracunaj_napako_1(visine, teze, y0, k):
    napake = 0
    for i in range(len(visine)):
        x = visine[i]
        y = teze[i]
        yfun = linearna_funkcija(k, y0, x)
        napake += abs(y - yfun)
    return napake

def izracunaj_napako_2(genders, visine, teze, y0, k):

    napake = 0
    for i in range(len(visine)):
        # Dobim visino (x) tocke
        x = visine[i]
        # Dobim tezo (y) tocke
        y = teze[i]
        # Spol tocke
        gender = genders[i]
        # Dobim visino trenutne premice
        yfun = linearna_funkcija(k, y0, x)

        # Izracunam razliko visin trenutne premice in tocke
        razlika_visin = y - yfun

        # Ce je tocka nad premico in ce je spol tocke zenska se napaka poveca
        if razlika_visin > 0 and gender == 'Female':
            napake += 1
        # Ce je tocka pod premico in ce je spol tocke moski se napaka poveca
        if razlika_visin < 0 and gender == 'Male':
            napake += 1

    # Ko ugotovim vsoto vseh papak vrnem vsoto napak.
    return napake

def ugotovi_spol(visino, tezo, y0_naj, k_naj):
    # Dobiva visino premice
    y_teze = linearna_funkcija(k_naj, y0_naj, visino)
    # Ugotoviva razliko med visino premice in visino tocke
    razlika_visin = tezo - y_teze
    # Ce je tocka nad premico je moski
    if razlika_visin > 0:
        return "moski"
    # Ce je tocka pod premico je zenska
    else:
        return "zenska"

# Odprem csv z podatki
file = open('data/weight-height.txt')

# Preberem vrstice csv-ja
vrstice = csv.DictReader(file)

# Ustvarim spiske kjer se bodo informacije shranjevale
heights = []
weights = []
genders = []

# Za vsako vrstico v vristicah
for vrstica in vrstice:
    # if row['Gender'] == 'Male':
    # Dodam informacije vrstice na konec spiskov
    genders.append(vrstica['Gender'])
    heights.append(float(vrstica['Height']))
    weights.append(float(vrstica['Weight']))

# Definiram spremenljivki k, y0 za trenutno premico ki jo probavam
k = 0
y0 = 0

# Definiram spremenljivki k_NAJ, y0_NAJ za najboljso premico ki jo najdem
k_naj = 0
y0_naj = 0

# Minimalna napaka najboljse premice
min_napaka = 10 ** 10

# Spisek vseh napak
napake = []
interval = 50

# Ponavaljam v neskoncnost
while True:
    # Izracunam napako za trenutno premico
    napaka = izracunaj_napako_2(genders, heights, weights, y0, k)
    # napaka = izracunaj_napako_1(heights, weights, y0, k)

    # Napako dodam v spisek napak
    napake.append(napaka)

    # Narisem vse pike (moskih, zenskih), trenutno premico in najboljso premico
    narisi(genders, heights, weights, y0, k, napake, y0_naj, k_naj)

    # Ce je napaka manjsa kot treutna najboljsa napaka sem najdla novo najboljso premico
    if napaka < min_napaka:
        min_napaka = napaka
        k_naj = k
        y0_naj = y0
        print(min_napaka, interval)

    # Iscem novo premico ki se jo testira za naslednji test
    k = k_naj + interval* (random.random() - 0.5)
    y0 = y0_naj + interval*(random.random() - 0.5)

    # Vsakic zmanjsam interval za 0.99 -> vsakic zmanjsam interval za 1%
    interval*= 0.99

    # Ko interval iskanja pade pod 0.01 se trening klasificiranja konca.
    if interval < 0.01:
        break


# V novi neskoncni zanki
while True:
    # Uprasamo uporabnika za tezo in visino
    teza = float(input("Vnesi tezo(lbs): "))
    visino = float(input("Vnesi visino(inch): "))
    # In na podlagi klasifikacije ugotovimo ali je uporabnik moski ali zenski
    print("Tvoj spol je:", ugotovi_spol(visino, teza, y0_naj, k_naj))