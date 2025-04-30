import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage
from sklearn.cluster import AgglomerativeClustering
import collections

# Step 1 --- Getting the data -----

# Loading the data
df = pd.read_csv('Final_HeroStone_Daraset.csv')

# Extracting relevant columns
X = df[['Type', 'Longitude', 'Latitude']]
place_date = df[['Name', 'Date']]

# Preparing data arrays
coordinates = X[['Latitude', 'Longitude']].values
names = place_date['Name'].values
dates = place_date['Date'].values
types = X['Type'].values

# Step 2: ---- Implementing hierarchical clustering ----

#This step will find all the hero-stones lying within ~1 kilometre of each other
#It assumes 1 degree of latitude/longitude = 111 km, which holds in Bengaluru (which is near the equator, where this relation holds)
linkage_data = linkage(coordinates, method='ward', metric='euclidean')
clustering = AgglomerativeClustering(n_clusters=None, linkage='ward', metric='euclidean', distance_threshold=0.009)
labels = clustering.fit_predict(coordinates)

# Analyze clusters
label_counts = collections.Counter(labels)
duplicates = np.array([label for label, count in label_counts.items() if count > 1])
max_cluster_size = max(label_counts.values())

print(f"Max cluster size: {max_cluster_size}")
print(f"Duplicate cluster labels: {duplicates}")
print(f"Max cluster label value: {max(labels)}")

# Step 3 --- Preparing output ------

cluster_names = []
cluster_dates = []
cluster_types = []
cluster_centers = []
coordinate_dict = {}

# Processing each cluster and saving to their sspecific arrays
for label in duplicates:
    indices = np.where(labels == label)[0]
    cluster_coords = coordinates[indices]
    cluster_center = np.mean(cluster_coords, axis=0)

    cluster_names.append(list(names[indices]))
    cluster_dates.append(list(dates[indices]))
    cluster_types.append(list(types[indices]))
    cluster_centers.append(cluster_center)
    coordinate_dict[label] = cluster_coords.T

# Converting lists to numpy arrays with padding
def pad_array(arr_list, max_len):
    return np.array([row + [0] * (max_len - len(row)) for row in arr_list], dtype=object)

max_len = max(len(row) for row in cluster_names)

cluster_names = pad_array(cluster_names, max_len)
cluster_dates = pad_array(cluster_dates, max_len)
cluster_types = pad_array(cluster_types, max_len)
cluster_centers = np.array(cluster_centers)

# Printing results
print("Cluster centers:\n", cluster_centers)
print("Cluster names:\n", cluster_names)
print("Cluster dates:\n", cluster_dates)
print("Cluster types:\n", cluster_types)
print("Coordinate dictionary:\n", coordinate_dict)

# Saving coordinate data
np.save('Check_Dictionary.npy', coordinate_dict)

#Also saving in an Excel sheet for ease of use
rows = []
center_rows = []

# Looping through each cluster to gather data
for i, label in enumerate(duplicates):
    indices = np.where(labels == label)[0]
    center_lat, center_lon = cluster_centers[i]

    # Saving cluster members
    for idx in indices:
        rows.append({
            "Cluster Label": int(label),
            "Name": names[idx],
            "Date": dates[idx],
            "Type": types[idx],
            "Latitude": coordinates[idx][0],
            "Longitude": coordinates[idx][1]
        })

    # Saving cluster center
    center_rows.append({
        "Cluster Label": int(label),
        "Center Latitude": center_lat,
        "Center Longitude": center_lon,
        "Cluster Size": len(indices)
    })

cluster_df = pd.DataFrame(rows)
centers_df = pd.DataFrame(center_rows)

# Writing to Excel with two sheets
output_file = "Clustered_Hero_Stones.xlsx"
with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
    cluster_df.to_excel(writer, index=False, sheet_name='HeroStone Clusters')
    centers_df.to_excel(writer, index=False, sheet_name='Cluster Centers')

print(f"Cluster data and centers saved to '{output_file}'")
