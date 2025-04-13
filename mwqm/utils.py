import ee
import geojson
import geopandas as gpd
import pandas as pd
import os
import geemap

CRS_EPSG = 4326


def gdf_to_fc(gdf: gpd.GeoDataFrame) -> ee.FeatureCollection:
    '''
    Converts a GeoDataFrame to an Earth Engine FeatureCollection, making
    sure that it is in the correct projection first.
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


def retrieve(features: ee.FeatureCollection, task: dict, tmp_dir: str ='') -> pd.DataFrame:
    '''
    Gets zonal statistics for an image from Earth Engine, loading it as a CSV.

    Parameters
    ----------
    features : ee.FeatureCollection or gpd.GeoDataFrame
        The features to get zonal statistics for
    task : dict
        A dictionary with keys 'image_id', 'band', and 'label'. Each of these
        should be a string. For example, the image_id for the JRC Global Surface
        Water dataset is "JRC/GSW1_4/GlobalSurfaceWater" and one of the bands is
        'occurrence'. The label is the name of the column in the output dataframe and
        we can freely choose what to call it.
    tmp_dir : str
        The directory to save the CSV file to
    img : ee.Image
        The image to get zonal statistics for. If None, the image will be retrieved
        from Earth Engine using the image_id in task. Helpful for getting derived quantities like slope.

    Returns
    -------
    zonal_df : pd.DataFrame
        A dataframe with a single column containing the zonal statistics for each feature in features
    '''
    out_path = os.path.join(tmp_dir, f'{task["label"]}.csv')

    if isinstance(features, gpd.GeoDataFrame):
        pre_existing_cols = features.columns
        features = gdf_to_fc(features)

    elif isinstance(features, ee.FeatureCollection):
        pre_existing_cols = features.getInfo()['features'][0]['properties'].keys()

    else:
        raise ValueError("features must be a GeoDataFrame or FeatureCollection")


    if not ('image' in task or 'image_id' in task):
        raise ValueError("task must contain either an 'image' or 'image_id' key")
    
    if "image" in task:
        img = task['image']
    else:
        img = ee.Image(task['image_id'])

    img = img.clip(features).select(task['band'])
    stat = task.get('stat', 'mean')

    # Since GEEMap downloads a file and doesn't allow for in-memory
    # retrieval, we just delete the file after we're done with it
    if task.get("is_group", False):
        geemap.zonal_statistics_by_group(
            img, 
            features, 
            statistics_type=stat,
            out_file_path=out_path)
    else:
        geemap.zonal_statistics(
            img, 
            features, 
            statistics_type=stat,
            out_file_path=out_path)

    zonal_df = pd.read_csv(out_path) \
        .drop('system:index', axis=1, errors='ignore') \
    
    # for each column, prepend the task label to the column name
    column_rename = lambda col: f'{task["label"]}_{col}' if col not in pre_existing_cols else col
    zonal_df.columns = [column_rename(col) for col in zonal_df.columns]
    os.remove(out_path)
    return zonal_df