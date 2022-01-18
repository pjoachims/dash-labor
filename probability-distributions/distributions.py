import numpy as np

from bokeh.layouts import column, row
from bokeh.plotting import figure
from bokeh.models import Button, CustomJS, Spinner, Select, CheckboxButtonGroup, RangeSlider, Div


class BokehDist:
    def __init__(self, *func_args, x_range=None, name=None, **func_kwargs):
        self.name = name
        self.func_args = func_args
        self.func_kwargs = func_kwargs
        
        # Handle args and kwargs
        on_change = Select(title="Update sliders by", value="value_throttled", options=["value", "value_throttled"], align='end')
        self.sliders = {}
        for param in [*func_args] + [*func_kwargs.values()]:
            if hasattr(param, "on_change"):
                param.on_change(on_change.value, self.update)
                self.sliders[param.title] = param
        self.options_other = {"on_change_slider": on_change}
        
        # Make figure
        if x_range is None:
            x_range = (-5, 5)
        self.fig = figure(
            x_range=x_range, 
            tools='reset,pan,box_zoom, ywheel_zoom, hover, save', 
            background_fill_color="#fafafa", 
            sizing_mode='scale_width',
            height=500,
        )
        self.fig.title.text_font_size = "3em"
        
        # X_range slider
        range_slider = RangeSlider(
            title="x-axis range",
            start=x_range[0] - 1,
            end=x_range[1] + 1,
            step=0.1,
            value=(self.fig.x_range.start, self.fig.x_range.end),
        )
        range_slider.js_link("value", self.fig.x_range, "start", attr_selector=0)
        range_slider.js_link("value", self.fig.x_range, "end", attr_selector=1)
        range_slider.on_change("value", self.update)
        self.sliders["xrange"] = range_slider
        
        # Slider adjusting
        slider_select = Select(title="Slider for", value=[*self.sliders.keys()][0], options=[*self.sliders.keys()])
        slider_prop = Select(title="Prop", value="start", options=["start", "end", "step"], align='end')
        slider_new_val = Spinner(title="Value", step=1e-6)
        slider_btn_adjust = Button(label="Update", button_type="success", align='end')
        def cb_update(new): 
            slider = self.sliders[slider_select.value]
            setattr(slider, slider_prop.value, slider_new_val.value)
            if not isinstance(slider, RangeSlider):
                if slider_prop.value == "start" and slider_new_val.value > getattr(slider, "value"):
                    setattr(slider, "value", slider_new_val.value)
                elif slider_prop.value == "end" and slider_new_val.value < getattr(slider, "value"):
                    setattr(slider, "value", slider_new_val.value)
        slider_btn_adjust.on_click(cb_update)
        self.opt_slider = {
            "param": slider_select,
            "property": slider_prop,
            "new_val": slider_new_val,
            "btn": slider_btn_adjust
        }
        



class BokehContDist(BokehDist):
    def __init__(self, sample_func, pdf, cdf, *func_args, x_range=None, name="", ppf=None, **func_kwargs):
        super().__init__(*func_args, x_range=x_range, name=name, **func_kwargs)
        self.sample_func = sample_func
        self.pdf = pdf
        self.cdf = cdf
        
        _init_args = [p.value if hasattr(p, "value") else p for p in func_args]    
        _init_kwargs = {k: (v.value if hasattr(v, "value") else v) for (k, v) in func_kwargs.items()}
        
        # Init plots
        samples = sample_func(*_init_args, size=1000, **_init_kwargs)
        hist, edges = np.histogram(samples, density=True, bins=50)
        histplot = self.fig.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], fill_color="lightgrey", line_color="white", legend_label="samples")
        x = np.linspace(self.fig.x_range.start, self.fig.x_range.end, 100)
        cdfplot = self.fig.line(x, cdf(x, *_init_args, **_init_kwargs), line_color="orange", line_width=2, legend_label="CDF")
        pdfplot = self.fig.line(x, pdf(x, *_init_args, **_init_kwargs), line_color="#1f77b4", line_width=2, legend_label="PDF")
        self.plots = {
            "pdf": pdfplot,
            "cdf": cdfplot,
            "hist": histplot,
        }
        
        # Sampling options
        # -> show / autoupdate / sample button
        sampling_checkboxes = CheckboxButtonGroup(labels=["Show", "Autoupdate"], active=[0, 1])
        def cb_sampling_checkboxes(attr, old, new):
            if 0 not in self.sampling["checkboxes"].active:
                self.plots["hist"].visible = False
            else:
                self.update(None, None, None)
                self.plots["hist"].visible = True
        def cb_sampling_run(new):
            return self.update(None, None, None, force_sampling=True)
        def cb_sampling_Nnbins(attr, old, new):
            self.sample_data(*self.func_args, **self.func_kwargs)
        sampling_checkboxes.on_change("active", cb_sampling_checkboxes)
        sampling_btn_run = Button(label="Sample", button_type="success", align='end')
        sampling_btn_run.on_click(cb_sampling_run)
        # -> sample size / number of bins for hist
        sampling_N = Spinner(title="Sample size", value=1000, step=50, low=1)
        sampling_N.on_change("value", cb_sampling_Nnbins)
        sampling_nbins = Spinner(title="Number of bins", value=50, low=1, step=5)
        sampling_nbins.on_change("value", cb_sampling_Nnbins)
        sampling_nbins.js_on_change(
            "value", 
            CustomJS(
                args=dict(histplot=histplot.glyph),
                code="""histplot.line_width = 1 / cb_obj.value"""
            ),
        )
        self.sampling = {
            "checkboxes": sampling_checkboxes,
            "btn_run": sampling_btn_run,
            "N": sampling_N,
            "nbins": sampling_nbins,
        }
        
        self.update(None, None, None)
        
    def update(self, attr, old, new, force_sampling: bool = False):
        func_args = [p.value for p in self.func_args]
        func_kw = {k: v.value for (k, v) in self.func_kwargs.items()}
        
        # Sample data
        if (0 in self.sampling["checkboxes"].active
                and (force_sampling or 1 in self.sampling["checkboxes"].active)):
            self.sample_data(*func_args, **func_kw)
        
        # Redo pdf/cdf
        self.update_dists(*func_args, **func_kw)

    def sample_data(self, *func_args, **func_kwargs):
        _args = [p.value if hasattr(p, "value") else p for p in func_args]    
        _kwargs = {k: (v.value if hasattr(v, "value") else v) for (k, v) in func_kwargs.items()}
        
        samples = self.sample_func(*_args, size=self.sampling["N"].value, **_kwargs)
        hist, edges = np.histogram(samples, density=True, bins=self.sampling["nbins"].value)
        self.plots["hist"].data_source.data = {"top": hist, "left": edges[:-1], "right": edges[1:]}
    
    def update_dists(self, *func_args, **func_kwargs):
        x = np.linspace(self.fig.x_range.start, self.fig.x_range.end, 1000)
        self.plots["pdf"].data_source.data = {"x": x, "y": self.pdf(x, *func_args, **func_kwargs)}
        self.plots["cdf"].data_source.data = {"x": x, "y": self.cdf(x, *func_args, **func_kwargs)}
    
    def get_layout(self):
        self.fig.legend.location = "top_left"
                
        layout = column(
            Div(text=f"<h2>{self.name}</h2>"),
            row(
                column(
                    self.fig, 
                    self.sliders["xrange"],
                ), 
                column(
                    Div(text=f"<br><em><u>Function parameters</u></em>"),
                    *self.func_args,
                    *self.func_kwargs.values(),
                    Div(text=f"<br><em><u>Sampling</u></em>"),
                    row(
                        self.sampling["checkboxes"],
                        self.sampling["btn_run"],
                        width=325,
                    ),
                    row(
                        self.sampling["N"],
                        self.sampling["nbins"],
                        width=325,
                    ),
                    Div(text=f"<br><em><u>Adjust sliders</u></em>"),
                    row(
                        self.opt_slider["param"],
                        self.opt_slider["property"],
                        self.opt_slider["new_val"],
                        self.opt_slider["btn"],
                        width=325,
                    ),
                    self.options_other["on_change_slider"],
                ),
            ),
        )
        return layout


class BokehDiscDist(BokehDist):
    def __init__(self, pmf, cdf, *func_args, x_range=None, name="", ppf=None, **func_kwargs):
        super().__init__(*func_args, x_range=x_range, name=name, **func_kwargs)
        self.pmf = pmf
        self.cdf = cdf
        
        _init_args = [p.value if hasattr(p, "value") else p for p in func_args]    
        _init_kwargs = {k: (v.value if hasattr(v, "value") else v) for (k, v) in func_kwargs.items()}
        
        # Init plots
        x = np.arange(np.floor(self.fig.x_range.start), np.ceil(self.fig.x_range.end))
        x_cdf = np.linspace(self.fig.x_range.start, self.fig.x_range.end, 1000)
        cdfplot = self.fig.line(x_cdf, cdf(x_cdf, *_init_args, **_init_kwargs), line_color="orange", line_width=2, legend_label="CDF")
        pmflines = self.fig.vbar(x, width=0.07, top=pmf(x, *_init_args, **_init_kwargs), line_color="#1f77b4", legend_label="pmf")
        pmfdots = self.fig.circle(x, pmf(x, *_init_args, **_init_kwargs), color="#1f77b4", radius=0.12)
        self.plots = {
            "pmf_lines": pmflines,
            "pmf_dots": pmfdots,
            "cdf": cdfplot,
            
        }
        
        self.update(None, None, None)
    
    def update(self, attr, old, new, force_sampling: bool = False):
        func_args = [p.value for p in self.func_args]
        func_kw = {k: v.value for (k, v) in self.func_kwargs.items()}
        
        # Redo pmf/cdf
        self.update_dists(*func_args, **func_kw)
    
    def update_dists(self, *func_args, **func_kwargs):
        x = np.arange(np.floor(self.fig.x_range.start), np.ceil(self.fig.x_range.end))
        x_cdf = np.linspace(self.fig.x_range.start, self.fig.x_range.end, 1000)
        self.plots["pmf_lines"].data_source.data = {"x": x, "top": self.pmf(x, *func_args, **func_kwargs)}
        self.plots["pmf_dots"].data_source.data = {"x": x, "y": self.pmf(x, *func_args, **func_kwargs)}
        self.plots["cdf"].data_source.data = {"x": x_cdf, "y": self.cdf(x_cdf, *func_args, **func_kwargs)}

    def get_layout(self):
        self.fig.legend.location = "top_left"
                
        layout = column(
            Div(text=f"<h2>{self.name}</h2>"),
            row(
                column(
                    self.fig, 
                    self.sliders["xrange"],
                ), 
                column(
                    Div(text=f"<br><em><u>Function parameters</u></em>"),
                    *self.func_args,
                    *self.func_kwargs.values(),
                    Div(text=f"<br><em><u>Adjust sliders</u></em>"),
                    row(
                        self.opt_slider["param"],
                        self.opt_slider["property"],
                        self.opt_slider["new_val"],
                        self.opt_slider["btn"],
                        width=325,
                    ),
                ),
            ),
        )
        return layout
