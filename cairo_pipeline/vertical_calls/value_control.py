"""
A Module of modular calls that can be made from layers through
the pdraw object
"""
import numpy as np
import cairo_utils as utils
import IPython

def pop_value(d, args, state, data):
    if args['var'] in data:
        the_list = data[args['var']]
    else:
        the_list = args['opts'][args['var']]
    if len(the_list) > 1:
        value = the_list.pop(0)
    else:
        value = the_list[0]
    data[args['var']] = the_list
    return (value, state, data)
