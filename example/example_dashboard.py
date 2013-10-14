"""
Example usage
"""

from pygauges import Application
from pygauges.displays import (ClockDisplay, VirualHorizonDisplay,
                               LinesDisplay)


app = Application()

surf = app.new_surface(300, 300)
app.add_display(ClockDisplay(surf), (10, 10))

surf = app.new_surface(300, 300)
app.add_display(VirualHorizonDisplay(surf), (340, 10))

surf = app.new_surface(800, 300)
app.add_display(LinesDisplay(surf), (10, 340))

app.mainloop()
