import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoModel, AutoTokenizer

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class CustomSBERT(nn.Module):
    def __init__(self, model_name="sberbank-ai/sbert_large_nlu_ru"):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.max_length = 256

        hidden = self.encoder.config.hidden_size

        self.bottleneck = nn.Sequential(
            nn.Linear(hidden, 256),
            nn.ReLU(),
            nn.Linear(256, hidden)
        )

    def pool(self, model_out, mask):
        token_embeddings = model_out[0]
        mask = mask.unsqueeze(-1)
        summed = torch.sum(token_embeddings * mask, dim=1)
        denom = torch.clamp(mask.sum(dim=1), min=1e-9)
        return summed / denom

    def encode(
            self,
            texts,
            device=DEVICE,
            batch_size=16
    ):
        with torch.no_grad():
            if isinstance(texts, str):
                texts = [texts]

            all_embeddings = []

            for i in range(0, len(texts), batch_size):
                chunk = texts[i:i + batch_size]

                batch = self.tokenizer(
                    chunk,
                    padding=True,
                    truncation=True,
                    max_length=self.max_length,
                    return_tensors="pt"
                )

                if device:
                    batch = {k: v.to(device) for k, v in batch.items()}

                out = self.encoder(**batch)
                pooled = self.pool(out, batch["attention_mask"])
                projected = self.bottleneck(pooled)
                emb = F.normalize(projected, p=2, dim=1)

                all_embeddings.append(emb.cpu())

            embeddings = torch.cat(all_embeddings, dim=0)

            return embeddings.numpy()


encoder = CustomSBERT()
