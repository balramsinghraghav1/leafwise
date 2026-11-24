import os
import time

from knowledge import display


class Predictor:
    """Loads the trained checkpoint (plant_model.pt) and classifies leaf images on the CPU/GPU."""

    def __init__(self, path: str):
        self.path, self.model, self.error, self.classes = path, None, None, []
        self.arch, self.gray = None, False
        self.load()

    def load(self):
        if not os.path.exists(self.path):
            self.error = (f"Model file not found at '{self.path}'. "
                          "Copy your trained plant_model.pt into the model/ folder and restart the app.")
            return
        try:
            import torch
            from torchvision import transforms
            from model_def import MEAN, STD, build_model
            ckpt = torch.load(self.path, map_location="cpu")
            self.classes = list(ckpt["classes"])
            self.arch, self.gray = ckpt["arch"], bool(ckpt.get("gray", False))
            m = build_model(self.arch, len(self.classes), pretrained=False)
            m.load_state_dict(ckpt["state_dict"])
            m.eval()
            self.tf = transforms.Compose([
                transforms.Resize((256, 256)), transforms.CenterCrop(224),
                transforms.ToTensor(), transforms.Normalize(MEAN, STD)])
            self.torch, self.model = torch, m
        except Exception as e:  # keep the site alive and show the reason on the Detect page
            self.model, self.error = None, f"Could not load the model: {e}"

    def crops(self):
        keys = sorted({c.partition("___")[0] for c in self.classes})
        return sorted(({"value": k, "name": display(k + "___x")["crop"]} for k in keys), key=lambda c: c["name"])

    def predict(self, img, crop=None, k=5):
        torch = self.torch
        if self.gray:
            from PIL import ImageOps
            img = ImageOps.grayscale(img).convert("RGB")
        x = self.tf(img).unsqueeze(0)
        t0 = time.perf_counter()
        with torch.no_grad():
            logits = self.model(x)[0]
        if crop:
            mask = torch.tensor([c.partition("___")[0] == crop for c in self.classes])
            if not bool(mask.any()):
                raise ValueError("That crop is not supported by the model.")
            logits = logits.masked_fill(~mask, float("-inf"))
            k = min(k, int(mask.sum()))
        probs = torch.softmax(logits, 0)
        vals, idx = torch.topk(probs, min(k, len(self.classes)))
        top = [{**display(self.classes[i]), "confidence": round(float(v), 4)}
               for v, i in zip(vals.tolist(), idx.tolist())]
        return {"top": top, "ms": round((time.perf_counter() - t0) * 1000)}
