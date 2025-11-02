import numpy as np

# Random Q, K, V matrices
def generate_random_qkv(seq_len=4, d_model=8):
    return [np.random.rand(seq_len, d_model) for _ in range(3)]

# Scaled dot-product attention
def self_attention(Q, K, V):
    d_k = Q.shape[-1]
    scores = np.dot(Q, K.T) / np.sqrt(d_k)
    weights = softmax(scores)
    output = np.dot(weights, V)
    return output, weights

def softmax(x):
    exp_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
    return exp_x / np.sum(exp_x, axis=-1, keepdims=True)

Q, K, V = generate_random_qkv()
out, attn_weights = self_attention(Q, K, V)
print("Attention Output:\n", out)
print("Attention Weights:\n", attn_weights)