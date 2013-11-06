"""Interact with functions using widgets.
"""

#-----------------------------------------------------------------------------
# Copyright (c) 2013, the IPython Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

from IPython.html.widgets import (init_widget_js, Widget, StringWidget,
    FloatRangeWidget, IntRangeWidget, BoolWidget, SelectionWidget,
    ContainerWidget)
from IPython.display import display, clear_output

#-----------------------------------------------------------------------------
# Classes and Functions
#-----------------------------------------------------------------------------


init_widget_js()


def _matches(o, pattern):
    if not len(o) == len(pattern):
        return False
    comps = zip(o,pattern)
    return all(map(lambda item: isinstance(item[0],item[1]), comps))


def _min_max_value(o):
    min = o[0]
    max = o[1]
    if not max > min:
        raise ValueError('max must be greater than min: (min={0}, max={1})'.format(min, max))
    value = min + abs(o[0]-o[1])/2
    return min, max, value

def _widget_abbrev(o):
    if isinstance(o, (str, unicode)):
        return StringWidget(value=unicode(o))
    elif isinstance(o, dict):
        values = map(unicode, o.keys())
        actual_values = o.values()
        w = SelectionWidget(value=values[0], values=values)
        w.actual_values = o
        return w
    elif isinstance(o, float):
        return FloatRangeWidget(value=o, min=-o, max=3.0*o)
    elif isinstance(o, int):
        return IntRangeWidget(value=o, min=-o, max=3*o)
    if isinstance(o, (list, tuple)):
        if _matches(o, (bool, bool)):
            # Has to be first as isinstance(True,int) == True
            return BoolWidget(value=o[0])
        elif _matches(o, (int, int)):
            min, max, value = _min_max_value(o)
            return IntRangeWidget(value=value, min=min, max=max)
        elif _matches(o, (int, int, int)):
            min, max, value = _min_max_value(o)
            return IntRangeWidget(value=value, min=min, max=max, step=o[2])
        elif _matches(o, (float, float)):
            min, max, value = _min_max_value(o)
            return FloatRangeWidget(value=value, min=min, max=max)
        elif _matches(o, (float, float, float)):
            min, max, value = _min_max_value(o)
            return FloatRangeWidget(value=value, min=min, max=max, step=o[2])
        elif _matches(o, (float, float, int)):
            min, max, value = _min_max_value(o)
            return FloatRangeWidget(value=value, min=min, max=max, step=float(o[2]))
        elif all(map(lambda x: isinstance(x, (str,unicode)), o)):
            return SelectionWidget(value=unicode(o[0]), values=map(unicode,o))


def interactive(f, **kwargs):
    """Interact with a function using widgets."""
    
    co = kwargs.pop('clear_output', True)
    # First convert all args to Widget instances
    widgets = []
    container = ContainerWidget()
    container.result = None
    container.arguments = dict()
    for key, value in kwargs.items():
        if isinstance(value, Widget):
            widget = value
        else:
            widget = _widget_abbrev(value)
            if widget is None:
                raise ValueError("Object cannot be transformed to a Widget")
        widgets.append((key,widget))
        widget.parent = container
    widgets = sorted(widgets, key=lambda e: e[1].__class__)
 
    # Build the callback
    def call_f(name, old, new):
        actual_kwargs = {}
        for key, widget in widgets:
            value = widget.value
            if hasattr(widget, 'actual_values'):
                value = widget.actual_values[value]
            container.arguments[key] = value
            actual_kwargs[key] = value
        if co:
            clear_output(wait=True)
        container.result = f(**actual_kwargs)

    # Wire up the widgets
    for key, widget in widgets:
        widget.on_trait_change(call_f, 'value')
        widget.description = key

    return container

def interact(f, **kwargs):
    w = interactive(f, **kwargs)
    display(w)
