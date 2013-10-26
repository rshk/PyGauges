"""
Example usage
"""

from pygauges import Application
from pygauges.displays import (ClockDisplay, VirualHorizonDisplay,
                               LinesDisplay)


app = Application(size=(1280, 1024))

app.add_display(ClockDisplay((300, 300)), (10, 10))
app.add_display(VirualHorizonDisplay((300, 300)), (340, 10))
app.add_display(LinesDisplay((1260, 300)), (10, 340))

app.mainloop()
