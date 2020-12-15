import torch

def CalculateLinkProbability(Node_i, Node_j):
    Node_i_T = torch.transpose(Node_i, 0, 0)
    scalar_prod_i_j = torch.dot(Node_i_T, Node_j)
    return torch.sigmoid(scalar_prod_i_j)

