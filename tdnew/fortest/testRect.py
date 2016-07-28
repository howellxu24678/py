# -*- coding: utf-8 -*-
__author__ = 'xujh'

import matplotlib.pyplot as plt
from matplotlib.patches import *
from matplotlib.collections import PatchCollection

def addRect(ax, list, **kwargs):
    patches = []

    patches.append(Rectangle((1.1, 2.1), 5, 2, fill=False,edgecolor=None,hatch='/'))
    patches.append(Rectangle((2.1, 3.1), 4, 1, fill=False,edgecolor=None,hatch='/'))

    # patches.append(Rectangle((1.1, 2.1), 5, 2, hatch='/'))
    # patches.append(Rectangle((2.1, 3.1), 4, 1, hatch='\\'))

    #collection = PatchCollection(patches, cmap=plt.cm.hsv, alpha=0.2)
    #collection = PatchCollection(patches, alpha=0.2)
    collection = PatchCollection(patches)
    ax.add_collection(collection)

    ax.grid(True)
    ax.autoscale_view()

def addRect2(ax, list, **kwargs):
    ax.add_patch(Rectangle((1.1, 2.1), 5, 2, fill=False, edgecolor='red', linestyle ='--'))
    ax.grid(True)
    ax.autoscale_view()

fig, ax = plt.subplots()
ax.set_title(u'矩形')
list = [1,2]
addRect2(ax, list, color='b')
plt.show()