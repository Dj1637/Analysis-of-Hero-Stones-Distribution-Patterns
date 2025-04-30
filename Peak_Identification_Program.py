import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import rasterio

# Loading hero-stone data
df = pd.read_csv('Final_HeroStone_Dataset.csv')
place_date = list(zip(df['Name'], df['Date']))
coordinates = list(zip(df['Latitude'], df['Longitude']))

# Step 1: --- Defining peak-checking function ---
def is_peak(dem: np.ndarray, row: int, col: int) -> bool:
    """Return True if the point at (row, col) is a peak in the DEM."""
    elevation = dem[row, col]

    # Defining the neighbourhood as a 3x3 grid around the point under consideration
    neighbours = [(-1, -1), (-1, 0), (-1, 1),
                 ( 0, -1),          ( 0, 1),
                 ( 1, -1), ( 1, 0), ( 1, 1)]

    for dr, dc in neighbours:

        # Getting the coordinates of the neighbour 
        nr, nc = row + dr, col + dc

        #Checking that the neighbour is within the bounds of the DEM
        if 0 <= nr < dem.shape[0] and 0 <= nc < dem.shape[1]:

            #Next step checks if the neighbouring point has a higher elevation than the point under consideration
            #If it does, the point is not a peak, so the loop is exited right away
            if dem[nr, nc] > elevation:
                return False

    #If no neighbouring point is higher than the point under consideration, it is a peak
    return True

# Step 2: --- Analyzing DEM and find peaks ---
peak_coords = []

with rasterio.open('output_SRTMGL1.tif') as src:
    dem = src.read(1)  # Load DEM as 2D array

    for i, (lat, lon) in enumerate(coordinates):
        try:
            row, col = src.index(lon, lat)
            elevation = dem[row, col]

            # For each coordinate, checking if it's a peak 
            if is_peak(dem, row, col):
                peak_coords.append((lat, lon)) #If it is, then it is appended to the peak_coords array
        except IndexError:
            print(f"Warning: Coordinate out of bounds - ({lat}, {lon})")

# Step 3: --- Output results ---
print(f"\n Number of peaks found: {len(peak_coords)}")
print("Peak Coordinates:")
for lat, lon in peak_coords:
    print(f"({lat}, {lon})")
