# Cairo Pipeline #

A Python Library to draw pipelines of commands, that are transformed into
stochastically sampled points. Inspired by Inconvergent.

## Dependencies ##

cairo, 
numpy,
[cairo_utils](https://github.com/jgrey4296/cairo_utils) library.

## Pipelines ##

The PDraw instance takes a pipeline to its .pipeline method.
Pipelines are lists of layers and their parameter dictionaries:
`
[ a_layer, {}, b_layer, {}, c_layer, {}]
`  

## Layers ##

Layers are functions, they take the pdraw instance, the options dictionary,
and a data dictionary passed from one layer to the next:
`
def a_layer(pdraw_instance, options):
    #Do something
`
  
## Crosscuts ##

Crosscuts are registered functions that hold their own state.
They are registered using the crosscuts.register_crosscuts layer.
Its options form is:
`
{ 'pairs' : { 'crosscut_call_name' : crosscut_function },
  'namespace' : 'optional_namespace' }
`

Crosscuts are called using `pdraw.call_crosscut(self, name, **kwargs)'

Crosscuts are functions of the form:
`
def crosscut_func(pdraw_instance, params, state):
	# do something
	return (output, updated_state)
`
