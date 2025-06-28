import torch
from torch.utils.data import DataLoader, TensorDataset
from torch import nn
from torch import optim
def synthetic_data(w,b,num):
    X=torch.normal(0,1,(num,len(w)))
    y=torch.matmul(X,w)+b
    y+=torch.normal(0,0.01,y.shape)
    return X,y.reshape(num,1)

true_w=torch.tensor([0.3,0.6,0.9])
true_b=torch.tensor(3.3)

features,labels = synthetic_data(true_w,true_b,10000)

dataset=TensorDataset(features,labels)
dataloader=DataLoader(dataset,100,shuffle=True)

# print(next(iter(dataloader)))

net = nn.Sequential(nn.Linear(3,12),nn.Linear(12,1))

loss = nn.MSELoss()

trainer = optim.SGD(net.parameters(),lr=0.1)


epochCount=10
for epoch in range(epochCount):
    for X, y in dataloader:
        l=loss(net(X),y)
        trainer.zero_grad()
        l.backward()
        trainer.step()
    l = loss(net(features),labels)
    print(f'epoch {epoch}, loss {l}')






