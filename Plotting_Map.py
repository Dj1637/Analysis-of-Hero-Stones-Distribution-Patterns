import pandas as pd
import numpy as np
import geopandas as gpd
import rasterio
import matplotlib.pyplot as plt
from rasterio.plot import show
from matplotlib.colors import Normalize
from mpl_toolkits.axes_grid1 import make_axes_locatable
import cmasher
import os

# Load the CSV file with coordinate points (latitude, longitude, name)
csv_file = 'Shorter_List_Hero_Stones.csv'  
data = pd.read_csv(csv_file)

# Convert the coordinates to a GeoDataFrame (lat/lon, EPSG:4326)
gdf = gpd.GeoDataFrame(data, geometry=gpd.points_from_xy(data['Longitude'], data['Latitude']), crs='EPSG:4326')

kml_output_folder = 'extracted_kml/'
kml_file = os.path.join(kml_output_folder, 'doc.kml')
ShapeMap = gpd.read_file(kml_file)

# Load the DEM from the TIFF file
dem_file = 'output_SRTMGL1.tif'  
with rasterio.open(dem_file) as src:
    dem = src.read(1)  # Read the first band (the DEM data)
    transform = src.transform
    crs = src.crs  # Coordinate reference system of the DEM
    bounds = src.bounds

# Reproject the GeoDataFrame to the CRS of the DEM (if necessary)
gdf = gdf.to_crs(crs)


Colour_Map = cmasher.get_sub_cmap(plt.cm.terrain, 0.25, 1.0, N=192)

# Plotting the DEM
fig, ax = plt.subplots(figsize=(10, 8))
show(dem, ax=ax, transform=transform, cmap=Colour_Map)
ShapeMap.plot(ax=ax, facecolor='none', edgecolor='black', linewidth=2) #Plotting the boundary of the district


# Create a colorbar for elevation
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="5%", pad=0.1)
norm = Normalize(vmin=dem.min(), vmax=dem.max())
cbar = plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=Colour_Map), cax=cax)
cbar.set_label('Elevation (meters)')

# Plot the coordinates and label them
for i, row in gdf.iterrows():
    # Get the transformed point (in DEM's CRS)
    lon, lat = row['geometry'].x, row['geometry'].y
    
    # Extract the pixel row, col from the DEM based on transformed coordinates
    row_idx, col_idx = src.index(lon, lat)
    elevation = dem[row_idx, col_idx]
    
    # Plot the point on the map and label it
    ax.scatter(lon, lat, color='red', s=30)
   
    #Uncomment the next line if the names are needed to be shown as well
    #ax.text(lon, lat, f'{row["Name"]} ({elevation}m)', fontsize=9, color='black', ha='right')

# Add title and labels
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")

# Show the map
plt.show()
