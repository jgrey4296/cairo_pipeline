# Cairo Splines #

A Python Library to draw pipelines of commands, that are transformed into
stochastically sampled points. Inspired by Inconvergent.

## Dependencies ##

cairo, 
numpy,
[cairo_utils](https://github.com/jgrey4296/cairo_utils) library.

## Pipeline requirements ##

Pipelines are functions:

`
def a_pipeline(pdraw_instance, data):
    return data
`

Pipelines are passed to pdraw_instance.pipeline as a list.
Data is customisable to pass to subsequent pipeline layers.

## Pipelines ##

### ExamplePipeline ###

### ColourPipeline ###

### RepeatLayer ###

### SandDeformation ###

### GraphPipeline ###

### BranchPipeline ###

### HyphaePipeline ###
