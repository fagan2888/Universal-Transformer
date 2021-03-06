import torch.nn as nn
import torch.nn.functional as fnn
import torch
import math

from model.attention import MultiHeadAttention
from model.residential import Residential
from model.embedding import PositionalEncoding


class UTransformerDecoder(nn.Module):
    def __init__(self, seq_len, d_model, h, dropout=0.5):
        super().__init__()
        self.attention = MultiHeadAttention(d_model, h)
        self.layer_norm = nn.LayerNorm(torch.Size([seq_len, d_model]))
        self.residential = Residential()
        self.dropout = nn.Dropout(dropout)
        self.transition = nn.Linear(d_model, d_model)
        self.pos_embedding = PositionalEncoding(d_model, seq_len)

    def forward(self, encoder_output, target, t, source_mask, target_mask):
        x, y = encoder_output, target

        y = self.pos_embedding(y, t)

        y = self.residential(y, self.attention(y, y, y, mask=target_mask))
        y = self.dropout(y)
        y = self.layer_norm(y)

        x = self.residential(y, self.attention(y, x, x, mask=source_mask))
        x = self.dropout(x)
        x = self.layer_norm(x)

        x = self.residential(x, self.transition(x))
        x = self.dropout(x)
        x = self.layer_norm(x)

        return x
