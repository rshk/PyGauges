"""
Miscellaneous default displays
"""

from collections import deque
import datetime
import math
import random
import time

import pygame

from .base import BaseDisplay, WithBackground
from .utils import colors, rescale, lazy_property


class ClockDisplay(WithBackground, BaseDisplay):
    """Just a clock, displaying time"""

    ## Style
    background_color = colors['base03']
    inner_background_color = colors['base02']
    border_color = colors['base0']
    border_width = 3
    needle_color = colors['base2']
    labels_color = colors['base00']
    draw_numbers = True

    @lazy_property
    def numbers_font(self):
        font_size = min(*self.size) / 20
        return pygame.font.SysFont(
            'Orbitron, monospace', font_size, True, False)

    def draw_background(self, surface):
        width, height = surface.get_width(), surface.get_height()
        radius = min(width, height) / 2
        center = (width / 2, height / 2)

        pygame.draw.circle(
            surface,
            self.inner_background_color,
            center,
            radius,
            0)  # width=0 -> fill
        pygame.draw.circle(
            surface,
            self.border_color,
            center,
            radius,
            self.border_width)

        for angle in xrange(0, 360, 6):
            rad_angle = math.radians(angle)

            dx = math.cos(rad_angle)
            dy = math.sin(rad_angle)

            x = center[0] + int(dx * (radius - 20))
            y = center[1] + int(dy * (radius - 20))

            if angle % 30 == 0:
                if self.draw_numbers:
                    hour = ((angle / 30) + 3) % 12
                    if hour == 0:
                        hour = 12
                    text = self.numbers_font.render(
                        str(hour), True, self.labels_color)
                    text_rect = text.get_rect()
                    text_rect.center = x, y
                    surface.blit(text, text_rect)

                else:
                    pygame.draw.circle(
                        surface,
                        self.labels_color, (x, y), 3, 0)

            else:
                x1 = center[0] + int(dx * (radius - 10))
                y1 = center[1] + int(dy * (radius - 10))
                x2 = center[0] + int(dx * (radius - 24))
                y2 = center[1] + int(dy * (radius - 24))
                pygame.draw.aaline(
                    surface, self.labels_color, (x1, y1), (x2, y2))

    def read_data(self):
        now = datetime.datetime.now()
        return (now.hour, now.minute, now.second)

    def draw(self, surface):
        hour, minute, second = self.read_data()

        width = surface.get_width()
        height = surface.get_height()
        radius = min(width, height) / 2
        center = (width / 2, height / 2)

        needles = [
            (((hour % 12) - 3) * 30, .8, colors['base2']),  # / 12 * 360
            ((minute - 15) * 6, 1, colors['base2']),  # / 60 * 360
            ((second - 15) * 6, 1, colors['base0'])  # / 60 * 360
        ]

        for value, length, color in needles:
            angle = math.radians(value)
            x = center[0] + int(math.cos(angle) * radius * length)
            y = center[0] + int(math.sin(angle) * radius * length)
            pygame.draw.aaline(
                surface, color, center, (x, y))


class VirualHorizonDisplay(WithBackground, BaseDisplay):
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

    def draw(self, surface):
        status = self.read_data()

        width, height = surface.get_width(), surface.get_height()
        pitch, roll = (math.radians(x) for x in status)
        radius = min(width, height) / 2
        center = (width / 2, height / 2)

        # First, we consider the pitch in order to decide
        # where to draw the line.
        # Then, use the roll to rotate it.

        horiz_h = center[1] + (math.sin(pitch) * radius)
        half_width = math.cos(pitch) * radius

        pygame.draw.aaline(
            surface,
            self.needle_pitch_color,
            (center[0] - half_width, horiz_h),
            (center[0] + half_width, horiz_h),
            self.needle_width)

        roll_h = math.cos(roll) * radius
        roll_v = math.sin(roll) * radius
        pygame.draw.aaline(
            surface,
            self.needle_roll_color,
            (center[0] - roll_h, center[1] - roll_v),
            (center[0] + roll_h, center[1] + roll_v),
            self.needle_width)


class LinesDisplay(WithBackground, BaseDisplay):
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

    @lazy_property
    def background_surface(self):
        surface = self.new_surface(alpha=False)
        self.draw_background(surface)
        return surface

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

    def draw(self, surface):
        status = self.read_data()

        for k, v in status.iteritems():
            self.lines[k].append(v)

        #self.surface.fill(colors['base03'])
        #self.surface.blit(self.background_surface, (0, 0))

        width, height = surface.get_width(), surface.get_height()
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

                if prev_point is not None:
                    pygame.draw.aaline(
                        surface,
                        self.line_colors[line_id],
                        prev_point,
                        (draw_x, draw_y))

                prev_point = (draw_x, draw_y)
                start_pos += x_units
