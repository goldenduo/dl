import torch
import os
import pandas as pd
dirPath= os.path.join("..","data")
os.makedirs(dirPath,exist_ok=True)
filePath = os.path.join(dirPath,"test.csv")
with open(filePath,"w") as f:
    f.write("name,age,height\n")
    f.write("Peter,18,180\n")
    f.write("Alan,23,199\n")
    f.write("Jay,23,NA\n")
csv=pd.read_csv(filePath)
data = csv.iloc[:,1:3]
# print(data.mean())
print(data.mode())
data.dropna(inplace=True)
nums=data.to_numpy()


print(nums)
print(nums.shape)
print(type(nums))
print(torch.tensor(nums))

