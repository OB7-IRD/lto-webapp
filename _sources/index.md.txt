---
html_theme.sidebar_secondary.remove:
sd_hide_title: true
---

<!-- CSS overrides on the homepage only -->
<style>
.bd-main .bd-content .bd-article-container {
  max-width: 70rem; /* Make homepage a little wider instead of 60em */
}
/* Extra top/bottom padding to the sections */
article.bd-article section {
  padding: 3rem 0 7rem;
}
/* Override all h1 headers except for the hidden ones */
h1:not(.sd-d-none) {
  font-weight: bold;
  font-size: 48px;
  text-align: center;
  margin-bottom: 4rem;
}
/* Override all h3 headers that are not in hero */
h3:not(#hero h3) {
  font-weight: bold;
  text-align: center;
}
</style>

(homepage)=
# Logbook to Observe

<div id="hero">

<div id="hero-left">  <!-- Start Hero Left -->
  <h2 style="font-size: 60px; font-weight: bold; margin: 2rem auto 0;">Logbook to Observe</h2>
  <h3 style="font-weight: bold; margin-top: 0;">A webapp that allow you to transfer logbook automatically into Observe</h3>
  <p>--</p>

<div class="homepage-button-container">
  <div class="homepage-button-container-row">
      <a href="./getting_started/index.html" class="homepage-button primary-button">Get Started</a>
      <a href="./user_guide/index.html" class="homepage-button secondary-button">User Guide</a>
  </div>
  <div class="homepage-button-container-row">
      <a href="./api/index.html" class="homepage-button-link">See API Reference →</a>
  </div>
</div>
</div>  <!-- End Hero Left -->

<div id="hero-right">  <!-- Start Hero Right -->

<!-- ::::::{grid} 1 2 2 2
:gutter: 3

:::::{grid-item-card}
:link: example_plot_trace_bars
:link-type: ref
:shadow: none
:class-card: example-gallery

:::{div} example-img-plot-overlay
Rank Bars Diagnostic with KDE using `plot_trace`
:::

:::{image} ./_images/mpl_plot_trace_bars.png
:::
:::::

:::::{grid-item-card}
:link: example_plot_forest_mixed
:link-type: ref
:shadow: none
:class-card: example-gallery

:::{div} example-img-plot-overlay
Forest Plot with ESS using `plot_forest`
:::

:::{image} ./_images/mpl_plot_forest_mixed.png
:::
:::::

:::::{grid-item-card}
:link: example_plot_dist
:link-type: ref
:shadow: none
:class-card: example-gallery

:::{div} example-img-plot-overlay
Dist Plot using `plot_dist`
:::

:::{image} ./_images/mpl_plot_dist.png
:::
:::::

:::::{grid-item-card}
:link: example_plot_density
:link-type: ref
:shadow: none
:class-card: example-gallery

:::{div} example-img-plot-overlay
Density Plot (Comparison) using `plot_density`
:::

:::{image} ./_images/mpl_plot_density.png
:::
:::::

:::::{grid-item-card}
:link: example_plot_pair
:link-type: ref
:shadow: none
:class-card: example-gallery

:::{div} example-img-plot-overlay
Pair Plot using `plot_pair`
:::

:::{image} ./_images/mpl_plot_pair.png
:::
:::::

:::::{grid-item-card}
:link: example_plot_ppc
:link-type: ref
:shadow: none
:class-card: example-gallery

:::{div} example-img-plot-overlay
Posterior Predictive Check Plot using `plot_ppc`
:::

:::{image} ./_images/mpl_plot_ppc.png
:::
:::::
:::::: -->

<!-- grid ended above, do not put anything on the right of markdown closings -->

</div>  <!-- End Hero Right -->
</div>  <!-- End Hero -->


<!-- Keep in markdown to generate headerlink -->
<!-- # Key Features -->

<!-- :::::{grid} 1 1 2 2
:gutter: 5

::::{grid-item-card}
:shadow: none
:class-card: sd-border-0

:::{image} _static/key_feature_interoperability.svg
:::

:::{div} key-features-text
<strong>Interoperability</strong><br/>
Integrates with all major probabilistic programming libraries: PyMC, CmdStanPy, PyStan, Pyro, NumPyro, and emcee.
:::
::::

::::{grid-item-card}
:shadow: none
:class-card: sd-border-0

:::{image} _static/key_feature_visualizations.svg
:::

:::{div} key-features-text
<strong>Large Suite of Visualizations</strong><br/>
Provides over 25 plotting functions for all parts of Bayesian workflow: visualizing distributions, diagnostics, and model checking. See the gallery for examples.
:::
::::

::::{grid-item-card}
:shadow: none
:class-card: sd-border-0

:::{image} _static/key_feature_diagnostics.svg
:::

:::{div} key-features-text
<strong>State of the Art Diagnostics</strong><br/>
Latest published diagnostics and statistics are implemented, tested and distributed with ArviZ.
:::
::::

::::{grid-item-card}
:shadow: none
:class-card: sd-border-0

:::{image} _static/key_feature_comparison.svg
:::

:::{div} key-features-text
<strong>Flexible Model Comparison</strong><br/>
Includes functions for comparing models with information criteria, and cross validation (both approximate and brute force).
:::
::::

::::{grid-item-card}
:shadow: none
:class-card: sd-border-0

:::{image} _static/key_feature_collaboration.svg
:::

:::{div} key-features-text
<strong>Built for Collaboration</strong><br/>
Designed for flexible cross-language serialization using netCDF or Zarr formats. ArviZ also has a [Julia version](https://julia.arviz.org/) that uses the same {ref}`data schema <schema>`.
:::
::::

::::{grid-item-card}
:shadow: none
:class-card: sd-border-0

:::{image} _static/key_feature_labeled_data.svg
:::

:::{div} key-features-text
<strong>Labeled Data</strong><br/>
Builds on top of xarray to work with labeled dimensions and coordinates.
:::
::::
::::: -->


```{toctree}
:maxdepth: 2
:hidden:
Getting Started<getting_started/index>
User Guide<user_guide/index>
API <api/index>

```
