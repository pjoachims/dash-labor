# Discrete distributions from scipy:
# bernoulli
# betabinom
# binom
# boltzmann
# dlaplace
# geom
# hypergeom
# logser
# nbinom
# nchypergeom_fisher
# nchypergeom_wallenius
# nhypergeom
# planck
# poisson
# randint
# skellam
# yulesimon
# zipf
# zipfian

from scipy.stats import binom, geom, hypergeom, nbinom, poisson

from bokeh.models import Slider
from bokeh.plotting import curdoc


from distributions import BokehDiscDist



binomdist = BokehDiscDist(
    binom.pmf, 
    binom.cdf, 
    Slider(start=1, end=40, value=10, step=1, title="n"),
    Slider(start=0, end=1, value=0.4, step=.01, title="p"),
    loc=Slider(start=-10, end=10, value=0, step=1, title="loc"),
    name="Binomial Distribution",
    x_range=(-0.2, 20.2),
)
curdoc().add_root(binomdist.get_layout())


geometric = BokehDiscDist(
    geom.pmf, 
    geom.cdf, 
    Slider(start=0, end=1, value=0.5, step=.01, title="p"),
    loc=Slider(start=-10, end=10, value=0, step=1, title="loc"),
    name="Geometric Distribution",
    x_range=(0.8, 10.2),
)
curdoc().add_root(geometric.get_layout())


hypergeometric = BokehDiscDist(
    hypergeom.pmf, 
    hypergeom.cdf, 
    Slider(start=0, end=30, value=20, step=1, title="M"),
    Slider(start=0, end=20, value=7, step=1, title="n"),
    Slider(start=0, end=30, value=12, step=1, title="N"),
    loc=Slider(start=-10, end=10, value=0, step=1, title="loc"),
    name="Hypergeometric Distribution",
    x_range=(-0.2, 20.2),
)
curdoc().add_root(hypergeometric.get_layout())



nbinomdist = BokehDiscDist(
    nbinom.pmf, 
    nbinom.cdf, 
    Slider(start=1, end=20, value=5, step=1, title="n"),
    Slider(start=0, end=1, value=0.5, step=.01, title="p"),
    loc=Slider(start=-10, end=10, value=0, step=1, title="loc"),
    name="Negative Binomial Distribution",
    x_range=(-0.2, 30.2),
)
curdoc().add_root(nbinomdist.get_layout())


poissondist = BokehDiscDist(
    poisson.pmf, 
    poisson.cdf, 
    Slider(start=0, end=3, value=1.5, step=.01, title="mu"),
    loc=Slider(start=-10, end=10, value=0, step=1, title="loc"),
    name="Possion Distribution",
    x_range=(-0.2, 10.2),
)
curdoc().add_root(poissondist.get_layout())


