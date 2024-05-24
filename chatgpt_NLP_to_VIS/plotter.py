import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the dataset
df = pd.read_csv("datasets/e7c00e40-4ab3-4d92-bf6a-24f92cd8d606.csv")

# Drop any rows with missing values
df.dropna(inplace=True)

# Create the Tree map visualization
plt.figure(figsize=(12, 6))
sns.set(style='whitegrid')
sns.scatterplot(x='Avg. Area House Age', y='Avg. Area Number of Rooms', size='Price', data=df, sizes=(20, 2000), legend=False)
plt.title('Tree map of Avg. Area House Age and Avg. Area Number of Rooms')
plt.xlabel('Avg. Area House Age')
plt.ylabel('Avg. Area Number of Rooms')
plt.savefig('tree_map.png')
plt.show()
