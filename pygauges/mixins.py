import pygame

from .utils import colors


class WithBackgroundMixin(object):
    """
    Mixin to be used for indicators that have a background
    layer to be rendered separately (for performance reasons,
    we keep the rendered surface and then just blit other stuff
    on top of it).
    """

    background_color = colors['base03']

    @property
    def background_surface(self):
        if getattr(self, '_background_surface', None) is None:
            self._background_surface = pygame.surface.Surface(
                self.surface_size)
            self.draw_background(self._background_surface)
        return self._background_surface

    def draw_background(self, surface):
        surface.fill(self.background_color)
