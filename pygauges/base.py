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
