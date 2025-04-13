import ee
import geojson
import geopandas as gpd
import json
import requests

CRS_EPSG = 4326
HUC_LENGTHS = {8, 10, 12}
NLDI_API_URL = "https://api.water.usgs.gov/nldi/linked-data/huc"

def gdf_to_fc(gdf: gpd.GeoDataFrame) -> ee.FeatureCollection:
    '''
    Turn a geopandas dataframe into an ee.FeatureCollection.
    '''
    gdf = gdf.to_crs(epsg=CRS_EPSG)
    all_polys = []
    for idx, row in gdf.iterrows():
        try:
            shpJSON = geojson.Feature(
                geometry=row['geometry'], 
                properties={key: value for key, value in row.items() if key != 'geometry'}
            )
            ee_feat = ee.Feature(shpJSON)
            all_polys.append(ee_feat)
        except Exception as e:
            print(f"feature {idx} is invalid: {e}")
    return ee.FeatureCollection(all_polys)

def get_watershed_boundary(huc: str) -> gpd.GeoDataFrame:
    '''
    Uses the NLDI API to get the watershed boundary for a given HUC.
    '''
    assert len(huc) in HUC_LENGTHS
    huc_length = len(huc)
    basin_url = f"{NLDI_API_URL}{huc_length}pp/{huc}/basin"
    try:
        print(f"  Requesting: {basin_url}")
        response = requests.get(basin_url)
        response.raise_for_status()
        return gpd.GeoDataFrame.from_features(response.json(), crs=CRS_EPSG)
    except requests.exceptions.RequestException as e:
        print(f"  Error making request for HUC {huc}: {e}")
        check_url = f"{NLDI_API_URL}{huc_length}pp/{huc}"
        try:
            check_response = requests.get(check_url)
            if check_response.status_code == 200:
                print(f"  HUC {huc} exists in the system, but basin data is not available")
            else:
                print(f"  HUC {huc} does not exist in the NLDI system (status code: {check_response.status_code})")
        except Exception as check_e:
            print(f"  Error checking HUC existence: {check_e}")
        return gpd.GeoDataFrame()
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        print(f"  Error parsing response for HUC {huc}: {e}")
        return gpd.GeoDataFrame()
