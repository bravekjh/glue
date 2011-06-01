import numpy as np

import cloudviz


class Subset(object):
    """Base class to handle subsets of data.

    These objects both describe subsets of a dataset, and relay any
    state changes to the hub that their parent data are assigned to.

    This base class only directly impements the logic that relays
    state changes back to the hub. Subclasses implement the actual
    description and manipulation of data subsets

    Attributes:
    -----------
    data: data instance
        The dataset that this subset describes
    style: dict
        A dictionary of visualization style properties (e.g., color)
        Clients are free to use this information when making plots.
    """

    class ListenDict(dict):
        """
        A small dictionary class to keep track of visual subset
        properties. Updates are broadcasted through the subset

        """
        def __init__(self, subset):
            dict.__init__(self)
            self._subset = subset

        def __setitem__(self, key, value):
            dict.__setitem__(self, key, value)
            self._subset.broadcast(self)

    def __init__(self, data):
        """ Create a new subclass object.

        This method should always be called by subclasses. It attaches
        data to the subset, and starts listening for state changes to
        send to the hub
        """
        self.data = data
        self._broadcasting = False
        self.style = self.ListenDict(self)
        self.style['color'] = 'r'

    def register(self):
        self.data.add_subset(self)
        self.do_broadcast(True)

    def do_broadcast(self, value):
        """
        Set whether state changes to the subset are relayed to a hub.

        It can be useful to turn off broadcasting, when modifying the
        subset in ways that don't impact any of the clients.

        Attributes:
        value: Whether the subset should broadcast state changes (True/False)

        """
        object.__setattr__(self, '_broadcasting', value)

    def broadcast(self, attribute=None):
        if not hasattr(self, '_broadcasting') \
                or not self._broadcasting or attribute == '_broadcasting':
            return
        elif self.data is not None and self.data.hub is not None:
            msg = cloudviz.message.SubsetUpdateMessage(self,
                                                       attribute=attribute)
            self.data.hub.broadcast(msg)

    def __setattr__(self, attribute, value):
        object.__setattr__(self, attribute, value)
        self.broadcast(attribute)


class TreeSubset(Subset):
    pass


class ElementSubset(Subset):

    def __init__(self, data):
        self.mask = np.zeros(data.shape, dtype=bool)
        Subset.__init__(self, data)

    def __setattr__(self, attribute, value):
        if hasattr(self, 'mask') and attribute == 'mask':
            if value.shape != self.data.shape:
                raise Exception("Mask has wrong shape")
        Subset.__setattr__(self, attribute, value)