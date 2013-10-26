"""
Base objects used in the application
"""

import warnings

import pygame

from .utils import lazy_property


class Drawable(object):
    """
    Base for the objects providing drawing functionality.

    Specifically, it has a surface on which it should draw
    itself. It also has an update() method that is called
    every time it is needed to refresh the drawing, plus
    a draw(surface) method that should be implemented to do
    the actual heavy lifting.
    """

    def __init__(self, size, **kwargs):
        """
        :param size:
            The size of the drawable space allocated
            to this widget.
        """
        self.size = size
        if len(kwargs):
            warnings.warn(
                'Unknown keyword arguments to drawable: {0}'.format(
                    ', '.join(kwargs.keys())))

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        if not isinstance(value, tuple) \
                or len(value) != 2 \
                or not all(isinstance(x, int) for x in value):
            raise ValueError("size must be a (width, height) tuple")
        self._size = value

    def on_size_change(self):
        # Should update the inner surface and make sure it's redrawn
        # next time it's requested
        del self._surface

    @property
    def width(self):
        return self.size[0]

    @property
    def height(self):
        return self.size[1]

    @property
    def surface(self):
        """
        Read-only property, returning a suitable surface
        containing the rendered contents of the drawable.
        """
        #self._surface.fill((0, 0, 0, 0))
        self.draw(self._surface)
        return self._surface

    @lazy_property
    def _surface(self):
        return self.new_surface()

    def new_surface(self, size=None, alpha=False):
        if size is None:
            size = self.size
        flags = 0
        if alpha:
            flags |= pygame.SRCALPHA
        return pygame.surface.Surface(size, flags=flags)

    def draw(self, surface):
        """
        Draw the widget contents on the specified surface
        """
        pass


class WithBackground(object):
    """
    Mixin to add support for a background layer.
    """

    background_color = (0, 0, 0)

    def on_size_change(self):
        del self._surface
        del self.background_surface
        del self.foreground_surface

    @lazy_property
    def background_surface(self):
        """
        The background surface doesn't change, a part from when
        the display is resized.
        """
        surface = self.new_surface(alpha=False)
        surface.fill(self.background_color)
        self.draw_background(surface)
        return surface

    @property
    def surface(self):
        """
        Property returning the surface, with all the layers stacked.
        """
        surface = self._surface
        surface.blit(self.background_surface, (0, 0))
        self.draw(surface)
        return surface

    def draw(self, surface):
        # todo: how do we check wheter the surface is already ok?
        pass

    def draw_background(self, surface):
        pass


class BaseDisplay(Drawable):
    """Base for all the display objects"""
