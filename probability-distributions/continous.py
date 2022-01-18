from scipy.stats import norm, beta, chi2, expon, gamma, laplace, t

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


beta = BokehContDist(
    beta.rvs, 
    beta.pdf, 
    beta.cdf, 
    Slider(start=0.1, end=10, value=3, step=.1, title="a"),
    Slider(start=0.1, end=10, value=3, step=.1, title="b"),
    x_range=(0, 1),
    name="Beta Distribution",
    loc=Slider(start=-10, end=10, value=0, step=.5, title="loc"),
    scale=Slider(start=0.1, end=10, value=1, step=.1, title="scale")
)
curdoc().add_root(beta.get_layout())


gamma_dist = BokehContDist(
    gamma.rvs, 
    gamma.pdf, 
    gamma.cdf, 
    Slider(start=0.01, end=10, value=1.99, step=.1, title="a"),
    x_range=(0, 12),
    name="Gamma Distribution",
    loc=Slider(start=-10, end=10, value=0, step=.5, title="loc"),
    scale=Slider(start=0.1, end=10, value=1, step=.1, title="scale")
)
curdoc().add_root(gamma_dist.get_layout())


laplace_dist = BokehContDist(
    laplace.rvs, 
    laplace.pdf, 
    laplace.cdf, 
    x_range=(-6, 6),
    name="Laplace Distribution",
    loc=Slider(start=-10, end=10, value=0, step=.5, title="loc"),
    scale=Slider(start=0.1, end=10, value=1, step=.1, title="scale")
)
curdoc().add_root(laplace_dist.get_layout())


t_dist = BokehContDist(
    t.rvs, 
    t.pdf, 
    t.cdf, 
    Slider(start=1, end=20, value=3, step=1, title="df"),
    name="Student's t Distribution",
    loc=Slider(start=-10, end=10, value=0, step=.5, title="loc"),
    scale=Slider(start=0.1, end=10, value=1, step=.1, title="scale"),
)
curdoc().add_root(t_dist.get_layout())


expon_dist = BokehContDist(
    expon.rvs, 
    expon.pdf, 
    expon.cdf, 
    name="Exponential Distribution",
    x_range=(-0.5, 4.5),
    loc=Slider(start=-10, end=10, value=0, step=.5, title="loc"),
    scale=Slider(start=0.1, end=10, value=1, step=.1, title="scale"),
)
curdoc().add_root(expon_dist.get_layout())


Chi2_dist = BokehContDist(
    chi2.rvs, 
    chi2.pdf, 
    chi2.cdf, 
    Slider(start=1, end=50, value=10, step=1, title="df"),
    name="Chi2 Distribution",
    x_range=(-5, 30),
    loc=Slider(start=-10, end=10, value=0, step=.5, title="loc"),
    scale=Slider(start=0.1, end=10, value=1, step=.1, title="scale"),
)
curdoc().add_root(Chi2_dist.get_layout())


curdoc().title = "Continous Probability Distributions"
