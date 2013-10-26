"""
Utilities to build a "gauges" panel to display some data.

Gauges act pretty much as real-life gauges, with a bunch
of inputs that can change, either actively or passively.

The idea is:

* We have a bunch of gauges that are drawn on the dashboard
* We have a bunch of sensors that are attached to gauge lines

Objects:

* Application -- acts as container for the whole thing;
  manages the main PyGame screen, rendering, etc.

* Dashboard -- a frame on which Displays can be placed.
  Manages layouting and rendering of the contained panels.

* Display -- an object responsible of drawing the current
  display on the given surface.
"""

import pygame

from .utils import colors, lazy_property


class ApplicationQuit(Exception):
    """Exception used to tell the application to quit"""
    pass


class Application(object):
    application_title = "PyGauges Dashboard"
    max_fps = 50
    show_fps = True
    default_window_size = 1280, 1024

    _fullscreen = False

    def __init__(self, size=None, fullscreen=False):

        pygame.init()
        pygame.display.set_caption(self.application_title)

        if fullscreen:
            self._fullscreen = True
            self._windowed_size = self.default_window_size
            self._fullscreen_size = size or max(pygame.display.list_modes())
            self.set_video_mode(self._fullscreen_size, True)

        else:
            self._fullscreen = False
            self._windowed_size = size or self.default_window_size
            self._fullscreen_size = max(pygame.display.list_modes())
            self.set_video_mode(self._windowed_size, False)

        ## Clock, for FPS calculation and stuff
        self.clock = pygame.time.Clock()

        ## List of displays to be drawn on this application
        self.displays = []

    @lazy_property
    def fps_font(self):
        ## Orbitron is a quite cool font, under Open Font License
        ## See: https://www.theleagueofmoveabletype.com/orbitron
        return pygame.font.SysFont('Orbitron, monospace', 20, True, False)

    def set_video_mode(self, resolution=None, fullscreen=False):
        """
        Change the current video mode.

        :param resolution:
            The new resolution to set, or None for autodiscover.
            If no resolution is specified, the last one for window/fullscreen
            will be used. If no fullscreen resolution is set, the largest
            available will be autoselect.
        :param fullscreen:
            Whether to go fullscreen or not.
        """
        screen_flags = pygame.DOUBLEBUF | pygame.RESIZABLE
        if fullscreen:
            screen_flags |= pygame.FULLSCREEN

        ## Store the fullscreen status in the object
        self._fullscreen = fullscreen

        if resolution is None:
            ## We want to use the previous resolution for the
            ## current fullscreen/windowed mode.
            if fullscreen:
                resolution = self._fullscreen_size
            else:
                resolution = self._windowed_size
        else:
            ## We store the new resolution for later reuse..
            if fullscreen:
                self._fullscreen_size = resolution
            else:
                self._windowed_size = resolution

        self.screen = pygame.display.set_mode(resolution, screen_flags)

    def mainloop(self):
        while True:
            try:
                self.process_events()
                self.draw()
                self.clock.tick(self.max_fps)
            except ApplicationQuit:
                return

    def process_events(self):
        for event in pygame.event.get():
            self.process_event(event)

    def process_event(self, event):
        if event.type == pygame.QUIT:
            raise ApplicationQuit()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                ## ESC means "quit"
                raise ApplicationQuit()

            elif event.key == pygame.K_F11:
                ## F11 means "toggle fullscreen"
                self.set_video_mode(fullscreen=not self._fullscreen)

            elif event.key == pygame.K_F5:
                ## F5 means "do a full refresh"

                # This is to make the screen "flash"
                self.screen.fill([0xff, 0xff, 0xff])
                pygame.display.flip()
                pygame.time.delay(40)

                # then, stuff will be refreshed automatically..

    def draw(self):
        ## Do a full redraw
        ## todo: avoid fully redrawing if not needed, for performance..
        self.screen.fill(colors['base03'])

        # Draw sensors on this screen
        for display in self.displays:
            # display['display'].draw()  # <- called by widget itself
            self.screen.blit(
                display['display'].surface,
                display['position'])

        # Draw FPS label
        fps = self.clock.get_fps()

        if fps >= 40:
            col = colors['green']
        elif fps >= 25:
            col = colors['yellow']
        else:
            col = colors['red']

        text = self.fps_font.render(
            " {:2d} FPS ".format(int(fps)), True, colors['base03'])
        text_rect = text.get_rect()
        text_rect.bottomleft = 0, self.screen.get_height()
        self.screen.fill(col, text_rect)
        self.screen.blit(text, text_rect)

        # Actually redraw the screen
        pygame.display.flip()

    def add_display(self, display, position):
        self.displays.append({
            'display': display,
            'position': position,
        })

    @property
    def screen_size(self):
        return (self.screen.get_width(),
                self.screen.get_height())

    def new_surface(self, width, height):
        #return pygame.surface.Surface((width, height), flags=pygame.SRCALPHA)
        return pygame.surface.Surface((width, height))

    def __del__(self):
        pygame.quit()
