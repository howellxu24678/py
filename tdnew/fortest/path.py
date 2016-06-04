__author__ = 'xujhao'
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches

verts = [
    (0., 0.), # left, bottom
    (1., 1.), # left, top
    (2., 1.), # right, top
    (3., 2.), # right, bottom
    #(0., 0.), # ignored
    ]

codes = [Path.MOVETO,
         Path.LINETO,
         Path.LINETO,
         Path.LINETO,
         #Path.LINETO,
         ]

path = Path(verts, codes)

fig = plt.figure()
ax = fig.add_subplot(111)
patch = patches.PathPatch(path, lw=1, facecolor='none')
ax.add_patch(patch)
ax.set_xlim(-2,3)
ax.set_ylim(-2,3)
plt.show()