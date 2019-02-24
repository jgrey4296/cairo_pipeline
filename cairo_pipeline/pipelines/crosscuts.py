import cairo_pipeline as cp
import cairo_pipeline.crosscuts as cc
import cairo_utils as utils
import numpy as np

standard = [ cp.misc.text.log_layer, { 'message' : 'Setting up crosscuts and random' }
             , cp.crosscuts.register_crosscuts, { 'pairs' : { 'pop' : cc.value_control.pop_value,
                                                              'access' : cc.value_control.value_access,
                                                              'store' : cc.value_control.value_store }}

             , cp.crosscuts.register_crosscuts, { 'namespace' : 'easing',
                                                  'pairs' : { 'call' : cc.easing.call,
                                                              'access' : cc.easing.access } }

             , cp.crosscuts.random.setup, { 'pairs': { "default" : cp.crosscuts.random.uniform,
                                                       "uniform" : cp.crosscuts.random.uniform,
                                                       "additive" : cp.crosscuts.random.additive } }
             ]
