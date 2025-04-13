# Research notes for MOTIVES water quality modeling, March 2025
- Primary goal is to produce a model of total nitrogen content in streamflow at an annual timescale (i.e. long-term average) using a simple model.
- This model should be capable of predicting changes in TN (total N) yield as a function of change in land cover
- Current approach is to use dataset of non-point source TN across USA to fit statistical model 

## Current plans and to-do list
- Finish downloading GEE dataset with modified JAXA Forest processing (classes instead of single band)
- Fit XGB and linear models with new dataset + interactions
- Incorporate suggested interactions from XGB model; compare performance
- Extend linear model to GAM using natural splines or similar
- Explore additional feature engineering:
    - land cover, slope, or other zonal stats within riparian buffer
    - sinuousity of river / channel morphology statistics
- Incorporate CDL data; this is available annually from 1997 onwards
- Consider making hierarchical across ecoregions

# Lit review notes:
- Allan 2004 review covers lots of interesting ways to approach feature engineering, e.g. ag within buffer zones