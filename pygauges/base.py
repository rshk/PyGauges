"""
Base objects used in the application
"""

import pygame
from .utils import colors


class Drawable(object):
    """
    Base for the objects providing drawing functionality.

    Specifically, it has a surface on which it should draw
    itself. It also has an update() method that is called
    every time it is needed to refresh the drawing, plus
    a draw(surface) method that should be implemented to do
    the actual heavy lifting.
    """

    def __init__(self, surface=None):
        self.set_surface(surface)

    @property
    def surface(self):
        ## It's a read-only property!
        return getattr(self, '_surface', None)

    @property
    def surface_size(self):
        return (self.surface.get_width(),
                self.surface.get_height())

    def set_surface(self, surface):
        self._surface = surface

    def update(self):
        """
        The update() method is used to ask the widget
        to update itself and return the inner surface.
        """
        self.draw(self.surface)
        return self.surface

    def draw(self, surface):
        """
        Draw the current display status on the surface.
        """
        pass


class MultiLayerDrawable(Drawable):
    layers = {
        'background': 10,
        'display': 50,
        'foreground': 90,
    }

    def __init__(self, *a, **kw):
        super(MultiLayerDrawable, self).__init__(*a, **kw)
        self._layers = dict((k, None) for k in self.layers)
        self._layers_dirty = dict((k, True) for k in self.layers)

    def set_surface(self, surface):
        super(MultiLayerDrawable, self).set_surface(surface)
        ## Recreate all surfaces for layers
        for layer in self.layers:
            self._layers[layer] = pygame.surface.Surface(self.surface_size)
            self._layers_dirty[layer] = True

    def draw(self, surface, force=False):
        ## Iterate the layers, sorted by layer position.
        ## Lower positions will float to the bottom.
        layers = sorted(self.layers.iteritems(), key=lambda x: x[1])
        for layer_id, layer_pos in layers:
            surface = self._layers[layer_id]
            ## Any caching is handled by the inner method
            self.draw_layer(layer_id, surface)

    def update_layer(self, name):
        """Allow for using custom methods to decide whether to update
        the layer or not"""

        method_name = 'layer_{}_needs_updating'.format(name)
        if self._layers_dirty[name]:
            pass
        if hasattr(self, method_name):
            result = getattr(self, method_name)(name)
        else:
            self.draw_layer(name)(self._layers[name])

    def draw_layer(self, name, surface, force=False):
        """Should call the appropriate method for drawing this layer"""

        method_name = 'draw_{}'.format(name)
        if hasattr(self, method_name):
            return getattr(self, method_name)(surface)


class BaseDisplay(Drawable):
    """Base for all the display objects"""

    pass
