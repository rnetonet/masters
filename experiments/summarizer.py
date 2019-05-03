import pandas as pd
import numpy as np
import sys

# Get columns
df = pd.read_csv(sys.argv[1])
print(df.columns)

cpu = df[df.columns[1]].mean()
print(cpu)
