from scipy.stats import norm

from bokeh.models import Slider
from bokeh.plotting import curdoc


from distributions import BokehContDist


normal = BokehContDist(
    norm.rvs, 
    norm.pdf, 
    norm.cdf, 
    name="Normal Distribution",
    loc=Slider(start=-10, end=10, value=0, step=.5, title="loc"),
    scale=Slider(start=0.1, end=10, value=1, step=.1, title="scale"),
)
curdoc().add_root(normal.get_layout())
