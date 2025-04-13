# Research notes for MOTIVES water quality modeling 
- Primary goal is to produce a model of total nitrogen content in streamflow at an annual timescale (i.e. long-term average) using a simple model
- Initial site to model will be Ft. Belvoir located at 38.701 N, -77.146 W (Fairfax County, VA)
- For now, SPARROW is the intended water quality model.

Here's an example API call for using the WQP API to get nitrogen data within 2 miles of Fort Belvoir:
```shell
curl -H "Accept: text/csv" -o wq.csv "https://www.waterqualitydata.us/data/Result/search?lat=38.701&long=-77.146&within=2&characteristic
```

This produces 5,722 records.



## Current plans and to-do list
- Identify 10+ sources of water quality data around Fairfax County
- For each location with data, get the catchments from DEM
- Get NLCD, slope data for the area
- Try to fit model with just these aforementioned values as well as some priors on instream processing rates and other parameters
- [Link(https://www.waterqualitydata.us/data/v3/api-docs)] to the Water Quality Portal API spec

Note: [Census of Agriculture claims](https://www.nass.usda.gov/Publications/AgCensus/2017/Online_Resources/County_Profiles/Virginia/cp51059.pdf) there is less than $1M USD in agriculture and <$200K USD in livestock in Fairfax county, 2017. This lets us rule out ag point source pollution


**Current blocker**
- Fitting the Sparrow model requires modeling the in-stream processing
- Candidate catchments are all much larger than Ft. Belvoir, and the creeks are very small
- In-stream processing rates will likely be quite different for FB, so the N data taken from the candidate sites was generated under a different process
- Simply modeling N runoff as a function of land cover will ignore the processing, leading us to underestimate the total N coming from a small catchment
- We would probably want to have 15+ stations to have # number of data points ~ # of parameters for fitting a model to land cover / environmental properties data

## Modeling notes:
SPARROW is a hybrid empirical/process‐based model for predicting mean annual constituent loads (e.g., total phosphorus) at water‐quality monitoring stations. It divides each watershed into subwatersheds (indexed by $i$) and further partitions each subwatershed into reach catchments (indexed by $j$). The predicted load at station $i$ is modeled as:

$$
\mu_i \;=\; \ln \Bigl(\sum_{n=1}^N \sum_{j=1}^{J_i} \beta_n\,S_{n,j}\,e^{-\alpha \, Z_j}\,H^S_{i,j}\,H^R_{i,j}\Bigr),
$$

where:

- $\mu_i$ is the natural logarithm of the mean annual load (e.g., $\ln(\text{tons yr}^{-1})$) at station $i$.  
- $n$ indexes each constituent source, out of $N$ total sources (point and nonpoint).  
- $\beta_n$ is the source‐specific export coefficient $\bigl[\text{tons P km}^{-2}\,\text{yr}^{-1}\bigr]$.  
- $S_{n,j}$ is the amount of source $n$ in reach $j$ $\bigl[\text{km}^2 \text{ for nonpoint sources, or tons yr}^{-1}\text{ for point sources}\bigr].$  
- $\alpha$ is a vector of dimensionless land‐to‐water delivery coefficients.  
- $Z_j$ is a vector of land‐surface characteristics for reach $j$.  
- $H^S_{i,j}$ is the fraction of constituent mass from reach $j$ remaining at station $i$ after in‐stream first‐order losses $\bigl[\text{dimensionless}\bigr].$  
- $H^R_{i,j}$ is the fraction of constituent mass from reach $j$ remaining at station $i$ after reservoir or lake first‐order losses $\bigl[\text{dimensionless}\bigr].$

Annual source mobilization is captured by $\beta_n\,S_{n,j}$, land‐to‐water delivery by $e^{-\alpha\,Z_j}$, and in‐stream and reservoir attenuation by $H^S_{i,j}$ and $H^R_{i,j}$. Typically, the model is calibrated to observed loads in a base year, accounting for interannual hydrologic variability.


# Lit review

#### Wang 2024
- The article "Riverine Nitrogen Data in the Conterminous United States by Yiming Wang et al. has a dataset [available here](https://doi.org/10.6084/m9.figshare.24645747) which has the total N yield for a very large number of catchments. However, the data is one-time and appears to have lots of missing values
- Within this dataset, the "Spatial Nitrogen Yield" table is likely most usable.
- A roadmap to using this data is as follows:
    - Get the predictors for each catchment
    - fit the model using the single N value for each catchment
    - Try to use the parameters to infer at a new location


#### Schwarz 2006
[Link here](https://digitalcommons.unl.edu/cgi/viewcontent.cgi?article=1171&context=usgspubs)
- Most comprehensive documentation from USGS, ~250 pages


#### Smith 1997
[Link here](https://www.neiwpcc.org/neiwpcc_docs/smith_others97.pdf)
They fit a national model using 414 stations' records. Here are the parameters they use:
| **Model Parameters**                       | **Coefficient Units<sup>a</sup>** |
|-------------------------------------------|-----------------------------------|
| **Nitrogen source** β                     |                                   |
| Point sources                              | dimensionless                     |
| Fertilizer application                     | dimensionless                     |
| Livestock waste production                 | dimensionless                     |
| Atmospheric deposition                     | dimensionless                     |
| Nonagricultural land                       | kg/ha/yr                          |
| **Land to water delivery** α               |                                   |
| Temperature                                | °F⁻¹                              |
| Slope<sup>c</sup>                          | %                                 |
| Soil permeability                          | h/cm                              |
| Stream density<sup>c</sup>                 | km⁻¹                              |
| Wetland<sup>d</sup>                        | dimensionless                     |
| Irrigated land<sup>e</sup>                 | dimensionless                     |
| Precipitation<sup>f</sup>                  | cm                                |
| Irrigated water use<sup>g</sup>            | cm                                |
| **In-stream decay** δ<sup>h</sup>          |                                   |
| δ₁ (Q < 28.3 m³/s)                         | d⁻¹                               |
| δ₂ (28.3 m³/s < Q < 283 m³/s)              | d⁻¹                               |
| δ₃ (Q > 283 m³/s)                          | d⁻¹                               |


#### Qian 2005
- [Link here](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2005WR003986)
- First to employ a Bayesian approach to calibrating the Sparrow model
- Employs a spatial random effect via conditional autoregressive prior to contribute to annual loading. Uses watershed adjacency to build adjacency matrix for CAR.
- the STSP formulation does not use the CAR, but instead uses a slightly different state space formulation where $Y_i \sim N(\mu_i, \sigma^2)$ but also $mu_i \sim N(f_i(\mu_{upstream}), \tau^2)$ where $\tau$ represents the standard deviation of the state-space innovation/error/jumps which are distinct from the observation error (with variance $\sigma^2$)


#### Wellen 2012
This work extends the Sparrow model to include temporal forcing factors to account for temporal variability in water quality. Also uses MCMC-based Bayesian approach.
- [Link here](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2012WR011821)
- Several model formulations are put forth:
    - For the SWALLOW formulation, The basic equations are $Y_{i,t} = \mu_i + W_{v,t} \nu_v + \epsilon _{i,t}$. 
    - Here, $\mu_{i}$ is the output of the Sparrow model at monitoring station $i$ (constant across years) while $W$ refers to the matrix of forcing factors varying over time and $\epsilon_{i,t}$ are IID Gaussian errors.
    - In SWALLOW II, $\mu$ is allowed to vary across time as well by letting the Sparrow model parameters vary in time.
    - Other model modifications include using a year-specific random effect which gets a Gaussian random walk prior.

#### Chambliss 2008
- This study is an MS thesis focused on applying PySparrow to a North Carolina catchment and comparing nutrient loads under a few land use scenarios.
- [Link here](https://dukespace.lib.duke.edu/server/api/core/bitstreams/8f81af07-15d1-4795-a3e1-b5b2308067c4/content)
- Introduces PySparrow and finds that regional recalibration needed for accuracy
- Focused on the Falls Lake Subbasin
- As described in this work, the national model uses 18 parameters:
    - One set for describing loads from upstream basins/pollutant inputs that drain directly to a catchment
    - One set for parameters describing landscape properties like soil permeability and drainage density which are land-to-water delivery factors
    - The last set of parameters govens stream decay processes like denitrification
- Differences between SPARROW and PySPARROW:
    - Former estimates long-term steady state total N and P loading while latter only handles total N loading and concentration in North Carolina. This may just be a consequence of the fact that they only studied North Carolina rather than an inherent model code limitation.
    - PySparrow uses 1:100,000 NHDPlus data for stream data while Sparrow uses 1:500,000 scale data from EPA Reach File 1
- PySparrow was run using National Land Cover Data at a 30 meter resolution.

#### Schwarz 2008
- [Link here](https://pmc.ncbi.nlm.nih.gov/articles/PMC3307635/)
- o1's summary:

    - The study takes a **national‐scale SPARROW model** for total nitrogen and total phosphorus and **tests whether model coefficients vary geographically**. The authors:

    1. **Partition** the conterminous US into three major basins (East, Northwest, Southwest).  
    2. **Estimate regional “fixed‐effects” models**, where each of the model’s process coefficients (sources, land‐to‐water delivery, aquatic attenuation) can differ by region.  
    3. **Compare** the prediction accuracy (e.g., reduction in RMSE) of the regional fixed‐effects models against the original **national** model.  
    4. **Impose cross‐region constraints** to pool information across regions and form a **“hybrid” model** with fewer free parameters, improving precision while retaining some regional specificity.  

    In practice, each regional coefficient $ \beta_{r} $ is tested against a weighted average of its “complement” regions’ estimates. If no statistically significant difference is found, $ \beta_{r} $ is constrained (equal) to that weighted average. All such constraints are then applied jointly, yielding the final hybrid model.  

    Results indicate:
    - **Fully regional** models slightly reduce overall prediction error but **inflate** coefficient uncertainty.  
    - **Hybrid** models partially preserve region‐specific terms while pooling data to **improve** coefficient precision.  
    - Most coefficients show **limited** evidence of strong regional variation, suggesting that fully independent regional models may be more flexible but less precise than models that use cross‐region constraints.