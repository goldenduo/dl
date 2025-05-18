import torch


if __name__ == '__main__':
    cuda_available = torch.cuda.is_available()
    print("cuda_available =", cuda_available)