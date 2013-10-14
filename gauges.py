"""
Utilities to build a "gauges" panel to display some data.

Gauges act pretty much as real-life gauges, with a bunch
of inputs that can change, either actively or passively.

The idea is:

* We have a bunch of gauges that are drawn on the dashboard
* We have a bunch of sensors that are attached to gauge lines
"""

from collections import deque
import datetime
import math
import random
import time

import pygame


## The Solarized color theme
colors = {
    'base03': (0x00, 0x2b, 0x36),
    'base02': (0x07, 0x36, 0x42),
    'base01': (0x58, 0x6e, 0x75),
    'base00': (0x65, 0x7b, 0x83),
    'base0': (0x83, 0x94, 0x96),
    'base1': (0x93, 0xa1, 0xa1),
    'base2': (0xee, 0xe8, 0xd5),
    'base3': (0xfd, 0xf6, 0xe3),
    'yellow': (0xb5, 0x89, 0x00),
    'orange': (0xcb, 0x4b, 0x16),
    'red': (0xdc, 0x32, 0x2f),
    'magenta': (0xd3, 0x36, 0x82),
    'violet': (0x6c, 0x71, 0xc4),
    'blue': (0x26, 0x8b, 0xd2),
    'cyan': (0x2a, 0xa1, 0x98),
    'green': (0x85, 0x99, 0x00),
}


def rescale(value, r1min, r1max, r2min, r2max, force_float=False):
    """
    Similar to C's ``map()``. Performs a value convertion
    between two scales.
    """
    return ((float(value - r1min) / (r1max - r1min)) * (r2max - r2min)) + r2min


class BaseDisplay(object):
    """
    Base for all the display objects.
    Mostly defines the base structure that displays should have:

    * Accept a surface as the first constructor argument

    * Has a .draw() method, called when an update of the surface
      is requested.
    """

    def __init__(self, surface):
        self.surface = surface

    @property
    def surface_size(self):
        return (self.surface.get_width(),
                self.surface.get_height())

    def draw(self):
        pass


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


class ClockDisplay(BaseDisplay, WithBackgroundMixin):
    """Just a clock, displaying time"""

    border_color = colors['base0']
    border_width = 3

    needle_color = colors['base2']

    labels_color = colors['base00']
    labels_color_lc = colors['base02']

    def draw_background(self, surface):
        width, height = surface.get_width(), surface.get_height()
        radius = min(width, height) / 2
        center = (width / 2, height / 2)

        surface.fill(colors['base03'])

        pygame.draw.circle(
            surface,
            self.border_color,
            center,
            radius,
            self.border_width)

        for angle in xrange(0, 360, 6):
            rad_angle = math.radians(angle)
            x = center[0] + int(math.cos(rad_angle) * (radius - 20))
            y = center[1] + int(math.sin(rad_angle) * (radius - 20))

            if angle % 30 == 0:
                color, width = self.labels_color, 3
            else:
                color, width = self.labels_color_lc, 1

            pygame.draw.circle(
                surface,
                color, (x, y), width, 0)

    def read_data(self):
        now = datetime.datetime.now()
        return (now.hour, now.minute, now.second)

    def draw(self):
        status = self.read_data()

        # If data was not changed, we can skip redrawing..
        if getattr(self, '_prev_data', None) == status:
            return
        self._prev_data = status

        # Draw a circle in the middle of the surface
        # todo: we might want to stack surfaces to speed up time..
        self.surface.fill(colors['base03'])
        self.surface.blit(self.background_surface, (0, 0))

        width = self.surface.get_width()
        height = self.surface.get_height()
        radius = min(width, height) / 2
        center = (width / 2, height / 2)

        now = datetime.datetime.now()
        needles = [
            (((now.hour % 12) - 3) * 30, .8, colors['base2']),  # / 12 * 360
            ((now.minute - 15) * 6, 1, colors['base2']),  # / 60 * 360
            ((now.second - 15) * 6, 1, colors['base0'])  # / 60 * 360
        ]

        for value, length, color in needles:
            angle = math.radians(value)
            x = center[0] + int(math.cos(angle) * radius * length)
            y = center[0] + int(math.sin(angle) * radius * length)
            # pygame.draw.line(
            #     self.surface, self.needle_color, center, (x, y), width)
            pygame.draw.aaline(
                self.surface, color, center, (x, y))


class VirualHorizonDisplay(BaseDisplay, WithBackgroundMixin):
    border_color = colors['base0']
    border_width = 1
    needle_pitch_color = colors['red']
    needle_roll_color = colors['yellow']
    needle_width = 1

    def draw_background(self, surface):
        width, height = surface.get_width(), surface.get_height()
        radius = min(width, height) / 2
        center = (width / 2, height / 2)
        surface.fill(colors['base03'])
        pygame.draw.circle(
            surface,
            self.border_color,
            center,
            radius,
            self.border_width)

    def read_data(self):
        # Returns the (pitch, roll) angle, in degrees
        # The horizontal position is (0, 0), angle ranges
        # are [-90..90].
        secs = time.time() % 60

        # todo: we could use some longer animation, to test
        #       more stuff...

        # Strategy for dummy data:

        def interpolate_val(ranges, cur_time):
            ## Interpolate a value from a time range
            for tstart, tend, vstart, vend in ranges:
                if tstart <= cur_time < tend:
                    # Find the percent position in the current range
                    delta_time = float(cur_time) - tstart
                    interval = tend - tstart
                    pos = delta_time / interval
                    # Get the actual desired value
                    val_delta = vend - vstart
                    return vstart + (pos * val_delta)

        pitch_changes = [
            # t_start, t_end, v_start, v_end
            (0, 20, 0, -60),
            (20, 30, -60, -60),
            (30, 40, -60, -30),
            (40, 60, -30, 0),
        ]

        roll_changes = [
            # t_start, t_end,  v_start, v_end
            (0, 10, 0, 0),
            (10, 30, 0, 60),
            (30, 50, 60, -60),
            (50, 60, -60, 0),
        ]

        pitch = interpolate_val(pitch_changes, secs)
        roll = interpolate_val(roll_changes, secs)

        return (int(pitch), int(roll))

    def draw(self):
        status = self.read_data()

        # If data was not changed, we can skip redrawing..
        if getattr(self, '_prev_data', None) == status:
            return
        self._prev_data = status

        self.surface.fill(colors['base03'])
        self.surface.blit(self.background_surface, (0, 0))

        width, height = self.surface_size
        pitch, roll = (math.radians(x) for x in status)
        radius = min(width, height) / 2
        center = (width / 2, height / 2)

        # First, we consider the pitch in order to decide
        # where to draw the line.
        # Then, use the roll to rotate it.

        horiz_h = center[1] + (math.sin(pitch) * radius)
        half_width = math.cos(pitch) * radius

        pygame.draw.line(
            self.surface,
            self.needle_pitch_color,
            (center[0] - half_width, horiz_h),
            (center[0] + half_width, horiz_h),
            self.needle_width)

        roll_h = math.cos(roll) * radius
        roll_v = math.sin(roll) * radius
        pygame.draw.line(
            self.surface,
            self.needle_roll_color,
            (center[0] - roll_h, center[1] - roll_v),
            (center[0] + roll_h, center[1] + roll_v),
            self.needle_width)


class LinesDisplay(BaseDisplay, WithBackgroundMixin):
    """
    A display showing a "lines" greaph
    """

    border_color = colors['base0']
    border_width = 1
    line_colors = {
        0: colors['green'],
        1: colors['red'],
        2: colors['violet'],
        3: colors['orange'],
        4: colors['blue'],
        5: colors['yellow'],
        6: colors['cyan'],
        7: colors['magenta'],
    }

    # Maximum stored values
    max_values = 300

    # Y axis range
    ymin, ymax = -20, 20

    # Amount of lines for this display
    lines_count = 8

    def __init__(self, *a, **kw):
        super(LinesDisplay, self).__init__(*a, **kw)

        self.lines = {}
        for i in xrange(self.lines_count):
            self.lines[i] = deque(maxlen=self.max_values)

    def _read_line(self, line_id, cur_time=None):
        if cur_time is None:
            cur_time = time.time()
        ang1 = math.radians(cur_time)
        if line_id == 0:
            return (math.sin(ang1 * 20) +
                    math.cos(ang1 * 667) +
                    math.cos(ang1 * 1024)) * 3 + 8
        if line_id == 1:
            return random.betavariate(3, 5) * 6 - 10
        if line_id == 2:
            return math.sin(ang1 * 60) * 18
        if line_id == 3:
            return math.cos(ang1 * 60) * 18
        if line_id == 4:
            return math.sin(ang1 * 240) * 10
        if line_id == 5:
            return math.cos(ang1 * 240) * 10
        if line_id == 6:
            return 1
        if line_id == 7:
            return (math.cos(ang1 * 1000) + math.cos(ang1 * 300)) * 4
        return 0  # other lines always read '0'

    def read_data(self):
        cur_time = time.time()
        data = {}
        for line_id in xrange(self.lines_count):
            data[line_id] = self._read_line(line_id, cur_time)
        return data

    def draw_background(self, surface):
        surface.fill(colors['base03'])
        pygame.draw.rect(surface, self.border_color, surface.get_rect(), 1)

    def draw(self):
        status = self.read_data()
        for k, v in status.iteritems():
            self.lines[k].append(v)

        self.surface.fill(colors['base03'])
        self.surface.blit(self.background_surface, (0, 0))

        width, height = self.surface_size
        x_units = float(width) / self.max_values

        ## Draw all the historical data
        for line_id, line_data in self.lines.iteritems():
            num_values = len(line_data)
            missing_values = self.max_values - num_values
            start_pos = missing_values * x_units
            prev_point = None

            for value in line_data:
                draw_x = start_pos
                draw_y = rescale(
                    value,
                    self.ymin,
                    self.ymax,
                    height, 0)

                #draw_y = height / 2 - value

                if prev_point is not None:
                    pygame.draw.aaline(
                        self.surface,
                        self.line_colors[line_id],
                        prev_point,
                        (draw_x, draw_y))

                prev_point = (draw_x, draw_y)
                start_pos += x_units


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

    def __del__(self):
        pygame.quit()


if __name__ == '__main__':
    app = Application()

    surf = pygame.surface.Surface((300, 300))
    app.add_display(ClockDisplay(surf), (10, 10))

    surf = pygame.surface.Surface((300, 300))
    app.add_display(VirualHorizonDisplay(surf), (340, 10))

    surf = pygame.surface.Surface((800, 300))
    app.add_display(LinesDisplay(surf), (10, 340))

    app.mainloop()
