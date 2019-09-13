"""
The Base Pipeline object, version 2
"""

from itertools import islice
import cairo_utils as utils
from cairo_utils import time as T
from . import constants

import logging as root_logger
logging = root_logger.getLogger(__name__)


class PDraw2:
    """ Runs a Pipeline.
    Pipelines are collections of layers.
    Layers call crosscuts defined by the pipeline.
    Layers are connected by channels.
    Layers are triggered by a time pattern.
    """

    def __init__(self, layers,
                 crosscuts, channels, timing,
                 crosscut_matrix, channel_matrix, time_matrix):
        #The current time
        self._now = None
        #The Layer Components, with initial setup. Dict
        self._layers = layers
        #Crosscuts used by layer components. Dict
        self._crosscuts = crosscuts
        #Communication channels between layers. Dict.
        self._channels = channels
        #Timing description for when layers fire. Pattern
        self._timing = timing

        #The connections
        #Layers -> Crosscuts
        self._crosscut_matrix = crosscut_matrix
        #Channels -> Layers -> Channels
        self._channel_matrix = channel_matrix
        # Events -> Layers
        self._time_matrix = time_matrix

        self.verify()

    def verify(self):
        #check all layers have an event trigger
        #check all channels are sources and sinks

        #get crosscut and channel enums from all layers,
        #ensure they have mappings

        #instantiate layers

    def tick(self, data=None):
        """ Tick the pipeline, progressing through the timing """
        #Get layer
        #enter layer
        #call layer
        #exit layer
        return None
