"""
Prototypes for Pipeline Version 2 Components
"""

class PipelineComponent:
    """ Superclass of all components """
    def __init__(self):
        return None


class BaseChannel(PipelineComponent):
    """ The Basic Channel Component.
    Used to connect layers, with controllable behaviour.
    ie: Can behave as FIFO, FILO, merge data, split data...
    Channels also fill the role of parameters to layers.
    """
    def __init__(self):
        self._data = None
        return None

    def _expect(self, value):
        return True

    def pull(self, value):
        return None

    def push(self, value):
        return None


class BaseCrossCut(PipelineComponent):
    """ The Basic CrossCut.
    Each Layer has defined gaps of functionality that must be filled.
    Crosscuts fill those and while the semantics can change in them,
    they do conform to the typing of the default implementation """
    def __init__(self):
        return None

    def _default(self, args):
        return None

    def __call__(self, args):
        return self._default(args)


class BaseLayer(PipelineComponent):
    """ The Basic Layer.
    Layers are a unit of functionality, with crosscuts left unspecified,
    to be detailed when the pipeline is defined.
    Layers do not communicate directly with each other, but use
    dedicated channels to pass messages

    Layers have internal enums of the crosscuts and channels they use,
    which are connected up in the pipeline.
    Layers can provide tests for what they expect from a channel or
    crosscut
    """
    def __init__(self):
        self._crosscuts = None
        self._pipeline = None
        self._connection_dict = None
        self._now = None

    def __enter__(self, pipeline, crosscut_dict, connection_dict, now):
        self._pipeline = pipeline
        self._crosscut_dict = crosscut_dict
        self._connection_dict = connection_dict
        self._now = now
        return self

    def __exit__(self, type, value, traceback):
        self._pipeline = None
        self._crosscut_dict = None
        self._connection_dict = None
        self._now = None
        return

    def crosscut(self, enum, args):
        crosscut = self._crosscut_dict[enum]
        return self._pipeline.call_crosscut(crosscut, args)

    def push(self, enum, data):
        channel = self._connection_dict[enum]
        channel.push(data)

    def pull(self, enum, data):
        channel = self._connection_dict[enum]
        return channel.pull(data)

    def expectation(self, enum):
        """ Return type expectation for channels and crosscuts """
        return lambda x: True

    def __call__(self):
        val = self.pull(channel)

        self.push(channel, val)

    def start(self):
        return None

    def stop(self):
        return None

    @staticmethod
    def get_crosscuts():
        #MUST return enum of crosscuts used
        raise Exception("Enums not defined yet")

    @staticmethod
    def get_channels():
        raise Exception("Channel enum not defined yet")

