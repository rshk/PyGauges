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
                self.surface_size, flags=pygame.SRCALPHA)

            self.draw_background(self._background_surface)
        return self._background_surface

    def draw_background(self, surface):
        surface.fill(self.background_color)


class WithChildrenMixin(object):
    """Drawable object with some children that needs drawing too.
    """

    ## Color palette
    background_color = (0, 0, 0)
    fps_label_colors = {
        'text': colors['base03'],
        'ok': colors['green'],
        'warning': colors['yellow'],
        'critical': colors['red']}

    @property
    def surface(self):
        pass

    @property
    def children(self):
        if self._children is None:
            self._children = []
        return self._children

    def draw(self):
        if self.surface is None:
            ## We don't have a surface on which to draw..
            return

        ## Do a full redraw
        self.surface.fill(self.background_color)

        ## Draw children on the surface
        for display in self.displays:
            display['display'].draw()
            self.surface.blit(
                display['display'].surface,
                display['position'])

        self.draw_fps_label()

        # Actually redraw the screen
        pygame.display.flip()

    def draw_fps_label(self):
        ## Draw FPS label
        fps = self.clock.get_fps()

        if fps >= 40:
            col = self.fps_label_colors['ok']
        elif fps >= 25:
            col = self.fps_label_colors['warning']
        else:
            col = self.fps_label_colors['critical']

        text = self.fps_font.render(
            " {:2d} FPS ".format(int(fps)), True, colors['base03'])
        text_rect = text.get_rect()
        text_rect.bottomleft = 0, self.surface.get_height()
        self.surface.fill(col, text_rect)
        self.surface.blit(text, text_rect)

    def add_child(self, display, position):
        """Add a child to this screen, at a given position"""
        self.children.append({
            'display': display,
            'position': position,
        })

    @property
    def screen_size(self):
        return (self.surface.get_width(),
                self.surface.get_height())

    def new_surface(self, width, height):
        return pygame.surface.Surface((width, height))

    def __del__(self):
        pygame.quit()
