"""
A Module of modular calls that can be made from layers through
the pdraw object
"""
import numpy as np
import cairo_utils as utils
import IPython

def pop_value(d, args, state):
    """ Initialise a list in persistent data, then pop off it """
    key= args['key']
    data = d.data()
    opts = args['opts']
    current_step = data['current_step']
    data_key = "{}_{}".format(current_step, key)
    if data_key in data:
        the_list = data[data_key]
    else:
        the_list = opts[key]

    if len(the_list) > 1:
        value = the_list.pop(0)
    else:
        value = the_list[0]

    d.set_data({data_key: the_list})
    return (value, state)


def cycle_value(d, args, state):
    """ Initialise a list in persistent data, then pop off it """
    key= args['key']
    data = d.data()
    opts = args['opts']
    current_step = data['current_step']
    data_key = "{}_{}".format(current_step, key)
    if data_key in data:
        the_list = data[data_key]
    else:
        the_list = opts[key]

    value = the_list.pop(0)
    the_list.append(value)

    d.set_data({data_key : the_list})
    return (value, state)

def value_access(d, args, state):
    """ Get a value from a pdraw's data, or a layers opts,
    with preference """
    data = d.data()
    keys = args['lookup']
    opts = args['opts']
    #fallback order
    order = [data, opts, state]
    if 'order' in args:
        lookup = {'opts' : opts, 'state': state, 'data': data}
        order = [lookup[x] for x in args['order']]
    # add defaults:
    order += [keys]
    vals = []
    sorted_keys = sorted(list(keys.keys()))
    for k in sorted_keys:
        found = False
        for x in order:
            if k in x:
                vals.append(x[k])
                found = True
                break
    return (vals, state)


def value_store(d, args, state):
    """ Store a value in the data or state """
    data = d.data()
    the_dict = args['pairs']
    target = args['target']

    if target == 'state':
        for k,v in the_dict.items():
            state[k] = v
    elif target == 'data':
        for k,v in the_dict.items():
            data[k] = v

    return (None, state)
