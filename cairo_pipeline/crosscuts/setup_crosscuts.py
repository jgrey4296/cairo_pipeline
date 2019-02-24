"""
Defines a layer to register vertical calls, within a pipeline
"""
def register_crosscuts(d, opts, data):
    """ A Simple layer to register a dictionary of functions into
    the draw object for use by later layers """
    namespace = None
    start_state = None
    if 'namespace' in opts:
        namespace = opts['namespace']
    if 'start_state' in opts:
        start_state = opts['start_state']
    d.register_crosscuts(opts['pairs'], namespace=namespace, start_state=start_state)
    return data
