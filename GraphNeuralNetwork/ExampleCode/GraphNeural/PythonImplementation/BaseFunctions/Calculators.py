import torch 

def LinkProbability(Node_i, Node_j):
    Node_i_T = torch.transpose(Node_i, 0, 0)
    scalar_prod_i_j = torch.dot(Node_i_T, Node_j)
    return float(torch.sigmoid(scalar_prod_i_j))

def TopologicalProbabilities(Results):
    Pairs = []
    for i_s in range(len(Results)):
        node_s_f = Results[i_s] 
        for i_r in range(len(Results)):
            node_r_f = Results[i_r]
            Prob = LinkProbability(node_s_f, node_r_f)
            Pairs.append([i_s, i_r, round(Prob, 6)])
    return Pairs
