# Overview

This project houses code and analyses related to national-scale water quality modeling using remotely sensed data and hierarchical Bayesian modeling to accurately calculate long-term average areal yields of total nitrogen export on a per-catchment basis at the HUC-12 level.

# Setup
Clone this repository and install using `pip install -e .`. If you wish to only install the dependencies required for fitting the model using MCMC with NumPyro (e.g. on a GPU server), you can use `pip install -r requirements-modeling` to install only the dependencies required to fit the model.