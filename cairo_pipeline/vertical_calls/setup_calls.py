"""
Defines a layer to register vertical calls, within a pipeline
"""
def register_calls(d, opts, data):
    """ A Simple layer to register a dictionary of functions into
    the draw object for use by later layers """
    for key,func in opts.items():
        d.register_call(key, func)
    return data
