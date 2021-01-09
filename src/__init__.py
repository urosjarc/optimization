import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import random

def linearna_funkcija(k, y0, x):
    return k * x + y0

def narisi(visine, teze, y0, k, napake, y0_naj, k_naj):
    x1 = 0
    x2 = 1
    y1 = linearna_funkcija(k, y0, x1)
    y2 = linearna_funkcija(k, y0, x2)
    y_naj_1 = linearna_funkcija(k_naj, y0_naj, x1)
    y_naj_2 = linearna_funkcija(k_naj, y0_naj, x2)

    plt.subplot(211)
    plt.plot(visine, teze, 'o')
    plt.plot([x1, x2], [y1, y2])
    plt.plot([x1, x2], [y_naj_1, y_naj_2])

    plt.subplot(212)
    plt.plot(napake, '-')

    plt.show(block=False)
    plt.pause(0.01)
    plt.clf()

def narisi_napake():
    z = []
    zmin = 10**8
    karr = []
    zmax = 0
    yarr = []
    for k in range(-25, 50, 1):
        print(k)
        z.append([])
        karr.append([])
        yarr.append([])
        for y0 in range(-2000, 1000, 5):
            yarr[-1].append(y0)
            karr[-1].append(k)
            z[-1].append(izracunaj_napako(heights, weights, y0, k))
        z_min = min(z[-1])
        z_max = max(z[-1])
        if zmin > z_min:
            zmin = z_min
        if zmax < z_max:
            zmax = z_max

    fig = plt.figure()
    ax = fig.gca(projection='3d')
    surf = ax.plot_surface(np.array(list(yarr)), np.array(list(karr)), np.array(list(z)), cmap=cm.coolwarm, linewidth=0, antialiased=False)
    fig.colorbar(surf, shrink=0.5, aspect=5)
    plt.show()

def izracunaj_napako(visine, teze, y0, k):
    napake = 0
    for i in range(len(teze)):
        x = visine[i]
        y = teze[i]
        yfun = linearna_funkcija(k, y0, x)
        napake += abs(y - yfun)
    return napake


if __name__ == '__main__':
    file = open('../data/weight-height.txt')
    heights = []
    weights = []
    for row in csv.DictReader(file):
                                        if row['Gender'] == 'Male':
                                        heights.append(float(row['Height']))
                                        weights.append(float(row['Weight']))

    #Normalizacija
    max_height = max(heights)
    max_weight = max(weights)
    heights = [e/max_height for e in heights]
    weights = [e/max_weight for e in weights]

    k = 0
    y0 = 0
    k_naj = 0
    y0_naj = 0
    min_napaka = 10**10
    napake = []
    i = 0

    hitrost = 100

    while True:
                   napaka = izracunaj_napako(heights, weights, y0, k)
                   napake.append(napaka)

                   narisi(heights, weights, y0, k, napake[len(napake)//2:], y0_naj, k_naj)
                   if napaka < min_napaka:
                   min_napaka = napaka
                   k_naj = k
                   y0_naj = y0
                   print(min_napaka, k, y0, hitrost)

                   k = k + hitrost*(random.random() - 0.5)
                   y0 = y0 + hitrost*(random.random() - 0.5)

                   if napaka-min_napaka > min_napaka/2:
                   k = k_naj
                   y0 = y0_naj
                   hitrost /= 2
                   i=1
                   # else:
                   #     hitrost *= 2

                   if i % 100 == 0:
                   k = k_naj
                   y0 = y0_naj
                   hitrost *= 2
                   i = 1

                   i+=1

