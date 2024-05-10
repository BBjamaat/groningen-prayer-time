# %%
import matplotlib.pyplot as plt
import os
import json
import pandas as pd


# %%
with open('../assets/times.json', 'r') as f:
    data = json.load(f)

# get the data
data = [
    d["data"] for d in data
]
# flatten the list
data = [item for sublist in data for item in sublist]

data = pd.DataFrame(data).drop("day", axis=1)


def to_minutes(x):
    a, b = x.split(":")
    return int(a) * 60 + int(b)


data = data.apply(lambda x: x.apply(to_minutes))
data
# %%
diff = data.diff()

diff.dropna().describe()
# %%

for col in data.columns:
    plt.plot(data[col], label=col)
plt.legend()
plt.show()

for col in diff.columns:
    plt.plot(diff[col], label=col + " diff")
plt.legend(loc="upper left")
plt.show()
# %%
