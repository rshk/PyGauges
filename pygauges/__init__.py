"""
Utilities to build a "gauges" panel to display some data.

Gauges act pretty much as real-life gauges, with a bunch
of inputs that can change, either actively or passively.

The idea is:

* We have a bunch of gauges that are drawn on the dashboard
* We have a bunch of sensors that are attached to gauge lines
"""

import pygame

from .utils import colors


class Dashboard(object):
    def __init__(self, surface):
        self.surface = surface

    def draw(self):
        pass


class ApplicationQuit(Exception):
    """Exception used to tell the application to quit"""
    pass


class Application(object):
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Gauges dashboard")
        screen_size = (1280, 1024)
        self.max_fps = 50
        self.screen = pygame.display.set_mode(screen_size, pygame.DOUBLEBUF)
        self.clock = pygame.time.Clock()
        self.displays = []

        self.fps_font = pygame.font.SysFont('monospace', 20, True, False)

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
                raise ApplicationQuit()

            elif event.key == pygame.K_F5:
                ## F5 means "do a full refresh"
                #_force_refresh = True

                # This is to make the screen "flash"
                self.screen.fill([0xff, 0xff, 0xff])
                pygame.display.flip()
                pygame.time.delay(40)

    def draw(self):
        ## Do a full redraw
        ## todo: avoid fully redrawing if not needed, for performance..
        self.screen.fill(colors['base03'])

        # Draw sensors on this screen
        for display in self.displays:
            display['display'].draw()
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
        return pygame.surface.Surface((width, height))

    def __del__(self):
        pygame.quit()
