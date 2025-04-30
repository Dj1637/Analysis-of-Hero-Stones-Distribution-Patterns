import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage
from sklearn.cluster import AgglomerativeClustering
import rasterio

# Loading hero-stone data
df = pd.read_csv('Shorter_List_Hero_Stones.csv')
place_date = list(zip(df['Name'], df['Date']))
coordinates = list(zip(df['Latitude'], df['Longitude']))

# --- Define trough-checking function ---
def is_trough(dem: np.ndarray, row: int, col: int) -> bool:
    """Return True if the point at (row, col) is a trough in the DEM."""
    elevation = dem[row, col]
    neighbors = [(-1, -1), (-1, 0), (-1, 1),
                 ( 0, -1),          ( 0, 1),
                 ( 1, -1), ( 1, 0), ( 1, 1)]

    for dr, dc in neighbors:
        nr, nc = row + dr, col + dc
        if 0 <= nr < dem.shape[0] and 0 <= nc < dem.shape[1]:
            if dem[nr, nc] < elevation:
                return False
    return True

# --- Analyze DEM and find troughs ---
trough_coords = []

with rasterio.open('output_SRTMGL1.tif') as src:
    dem = src.read(1)  # Load DEM as 2D array

    for i, (lat, lon) in enumerate(coordinates):
        try:
            row, col = src.index(lon, lat)
            elevation = dem[row, col]

            if is_trough(dem, row, col):
                trough_coords.append((lat, lon))
        except IndexError:
            print(f"Warning: Coordinate out of bounds - ({lat}, {lon})")

# --- Output results ---
print(f"\n Number of troughs found: {len(trough_coords)}")
print("Trough Coordinates:")
for lat, lon in trough_coords:
    print(f"({lat}, {lon})")
