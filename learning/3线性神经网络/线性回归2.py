import torch
import random


def synthetic_data(w, b, num):
    X = torch.normal(0, 1, (num, len(w)))
    y = torch.matmul(X, w) + b + torch.normal(0, 0.01, (num,))
    return X, y


true_w = torch.tensor([0.524, 0.643])
true_b = -9.74
num_examples = 1000
features, labels = synthetic_data(true_w, true_b, num_examples)

print(f'features.shape: {features.shape}')
print(f'labels.shape: {labels.shape}')


def data_iter(features, labels, batch_size):
    length = len(labels)
    indices=list(range(length))
    random.shuffle(indices)
    for i in range(0,length,batch_size):
        batch_indices=torch.tensor(indices[i:min(i+batch_size,length)])
        yield features[batch_indices], labels[batch_indices]

def net(X,w,b):
    return torch.matmul(X,w) + b
def loss(y_hat,y):
    return (y_hat-y.reshape(y_hat.shape))**2/2

def sgd(params, l):
    with torch.no_grad():
        for param in params:
            param-= l * param.grad
            param.grad.zero_()

lr=0.01
count_epoch=100
compute_w=torch.normal(0,1,(2,1),requires_grad=True)
compute_b=torch.zeros(1,requires_grad=True)

for epoch in range(count_epoch):
    for X,y in data_iter(features, labels, batch_size=20):
        y_hat=net(X,compute_w,compute_b)
        l=loss(y_hat,y)
        l.mean().backward()
        sgd([compute_w,compute_b],lr)
    with torch.no_grad():
        print(f'----epoch: {epoch}')
        print(f'compute_w: {compute_w}')
        print(f'compute_b: {compute_b}')
        print(f'true_w: {true_w}')
        print(f'true_b: {true_b}')
        l=loss(net(features,compute_w,compute_b),labels).mean()
        print(f'loss: {l}')




