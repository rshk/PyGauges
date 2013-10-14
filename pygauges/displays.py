"""
Miscellaneous default displays
"""

from collections import deque
import datetime
import math
import random
import time

import pygame

from .base import BaseDisplay
from .mixins import WithBackgroundMixin
from .utils import colors, rescale


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
