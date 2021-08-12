"""

You can enable picking by setting the "picker" property of an artist
(for example, a matplotlib Line2D, Text, Patch, Polygon, AxesImage,
etc...)

There are a variety of meanings of the picker property

    None -  picking is disabled for this artist (default)

    boolean - if True then picking will be enabled and the
      artist will fire a pick event if the mouse event is over
      the artist

    float - if picker is a number it is interpreted as an
      epsilon tolerance in points and the artist will fire
      off an event if it's data is within epsilon of the mouse
      event.  For some artists like lines and patch collections,
      the artist may provide additional data to the pick event
      that is generated, for example, the indices of the data within
      epsilon of the pick event

    function - if picker is callable, it is a user supplied
      function which determines whether the artist is hit by the
      mouse event.

         hit, props = picker(artist, mouseevent)

      to determine the hit test.  If the mouse event is over the
      artist, return hit=True and props is a dictionary of properties
      you want added to the PickEvent attributes


After you have enabled an artist for picking by setting the "picker"
property, you need to connect to the figure canvas pick_event to get
pick callbacks on mouse press events.  For example,

  def pick_handler(event):
      mouseevent = event.mouseevent
      artist = event.artist
      # now do something with this...


The pick event (matplotlib.backend_bases.PickEvent) which is passed to
your callback is always fired with two attributes:

  mouseevent - the mouse event that generate the pick event.  The
    mouse event in turn has attributes like x and y (the coordinates in
    display space, such as pixels from left, bottom) and xdata, ydata (the
    coords in data space).  Additionally, you can get information about
    which buttons were pressed, which keys were pressed, which Axes
    the mouse is over, etc.  See matplotlib.backend_bases.MouseEvent
    for details.

  artist - the matplotlib.artist that generated the pick event.

Additionally, certain artists like Line2D and PatchCollection may
attach additional meta data like the indices into the data that meet
the picker criteria (for example, all the points in the line that are within
the specified epsilon tolerance)

The examples below illustrate each of these methods.
"""

from __future__ import print_function
import matplotlib.pyplot as plt
import numpy as np

if 1:  # picking on a scatter plot (matplotlib.collections.RegularPolyCollection)


    def onpick3(event):
        ind = event.ind
        print('onpick3 scatter:', ind, np.take(ra, ind), np.take(dec, ind))

    coords = np.load('coords.npy')
    ra = coords[:,0]
    dec = coords[:,1]
    
    s=1 
    color='blue'    
    org=0
    projection="mollweide"
    size=(10, 6.180)

    x = np.remainder(ra + 360 - org, 360)
    ind = x > 180
    x[ind] -= 360
    x = -x

    fig = plt.figure(1, figsize=size)

    ax = fig.add_subplot(111, projection=projection)
    ax.scatter(np.radians(x), np.radians(dec), color=color, s=s, rasterized=True, picker=True)
    ax.grid(True, color="k", linestyle="dashed", alpha=0.1)
    ax.set_longitude_grid(45)  # deg
    ax.set_latitude_grid(45)
    ax.set_longitude_grid_ends(90)
    tick_labels = np.array([r"135°", r"90°", r"45°", r"0°", r"315°", r"270°", r"225°"])
    ax.set_xticklabels(tick_labels)

    plt.tight_layout()

    fig.canvas.mpl_connect('pick_event', onpick3)

plt.show()