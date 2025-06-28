import torch





if __name__ == '__main__':
    if torch.cuda.is_available():
        print("CUDA available ")
    if torch.backends.mps.is_available():
        print("MPS available ")