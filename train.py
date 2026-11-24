"""Train AlexNet / GoogLeNet on PlantVillage (Mohanty et al. 2016 setup).

Example (Colab / local GPU):
  git clone --depth 1 https://github.com/spMohanty/PlantVillage-Dataset
  python train.py --data PlantVillage-Dataset/raw/color --arch googlenet --mode transfer --epochs 10
Use raw/grayscale + --gray, or raw/segmented, for the other two image versions.
All images of the same leaf (same file-name prefix before '___') stay in one split.
"""
import argparse
import os
import random

import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import classification_report
from sklearn.model_selection import GroupShuffleSplit
from torch.utils.data import DataLoader, Dataset
from torchvision import datasets, transforms

from model_def import ARCHS, MEAN, STD, build_model

p = argparse.ArgumentParser()
p.add_argument("--data", required=True, help="folder with one sub-folder per class")
p.add_argument("--arch", choices=ARCHS, default="googlenet")
p.add_argument("--mode", choices=["scratch", "transfer"], default="transfer")
p.add_argument("--epochs", type=int, default=10)
p.add_argument("--batch", type=int, default=32)
p.add_argument("--lr", type=float, default=None)
p.add_argument("--train-ratio", type=float, default=0.8, help="0.8 = 80-20 split ... 0.2 = 20-80")
p.add_argument("--gray", action="store_true", help="convert images to grayscale")
p.add_argument("--fraction", type=float, default=1.0, help="use a fraction of data for quick tests")
p.add_argument("--workers", type=int, default=2)
p.add_argument("--out", default="model/plant_model.pt")
p.add_argument("--seed", type=int, default=42)


class Split(Dataset):
    def __init__(self, base, idx, tf):
        self.base, self.idx, self.tf = base, idx, tf

    def __len__(self):
        return len(self.idx)

    def __getitem__(self, i):
        path, y = self.base.samples[self.idx[i]]
        return self.tf(self.base.loader(path)), y


def main():
    a = p.parse_args()
    random.seed(a.seed); np.random.seed(a.seed); torch.manual_seed(a.seed)
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    base = datasets.ImageFolder(a.data)
    n = len(base.samples)
    print(f"{n} images, {len(base.classes)} classes, device={dev}")

    groups = np.array([os.path.basename(s[0]).split("___")[0] for s in base.samples])
    ids = np.arange(n)
    if a.fraction < 1:
        ids = np.random.choice(n, int(n * a.fraction), replace=False)
    tr, te = next(GroupShuffleSplit(1, train_size=a.train_ratio, random_state=a.seed)
                  .split(ids, groups=groups[ids]))
    tr_idx, te_idx = ids[tr], ids[te]
    assert not set(groups[tr_idx]) & set(groups[te_idx]), "leaf leakage between splits"
    print(f"train={len(tr_idx)} test={len(te_idx)} (no shared leaves)")

    pre = [transforms.Grayscale(3)] if a.gray else []
    tf_train = transforms.Compose(pre + [
        transforms.Resize((256, 256)), transforms.RandomCrop(224),
        transforms.RandomHorizontalFlip(), transforms.RandomVerticalFlip(),
        transforms.RandomRotation(25), transforms.ColorJitter(0.25, 0.25),
        transforms.ToTensor(), transforms.Normalize(MEAN, STD)])
    tf_test = transforms.Compose(pre + [
        transforms.Resize((256, 256)), transforms.CenterCrop(224),
        transforms.ToTensor(), transforms.Normalize(MEAN, STD)])
    kw = dict(batch_size=a.batch, num_workers=a.workers, pin_memory=dev.type == "cuda")
    tl = DataLoader(Split(base, tr_idx, tf_train), shuffle=True, **kw)
    vl = DataLoader(Split(base, te_idx, tf_test), shuffle=False, **kw)

    model = build_model(a.arch, len(base.classes), a.mode == "transfer").to(dev)
    lr = a.lr or (3e-4 if a.mode == "transfer" else 1e-3)
    opt = torch.optim.AdamW(model.parameters(), lr=lr)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, a.epochs)
    loss_fn = nn.CrossEntropyLoss()
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    best = 0.0

    def evaluate():
        model.eval(); ys, ps = [], []
        with torch.no_grad():
            for x, y in vl:
                ps += model(x.to(dev)).argmax(1).cpu().tolist(); ys += y.tolist()
        return np.array(ys), np.array(ps)

    for ep in range(1, a.epochs + 1):
        model.train(); tot = 0.0
        for x, y in tl:
            x, y = x.to(dev), y.to(dev)
            opt.zero_grad()
            loss = loss_fn(model(x), y)
            loss.backward(); opt.step(); tot += loss.item() * len(y)
        sched.step()
        ys, ps = evaluate(); acc = float((ys == ps).mean())
        print(f"epoch {ep}/{a.epochs}  loss={tot / len(tr_idx):.4f}  test_acc={acc:.4f}")
        if acc >= best:
            best = acc
            torch.save({"arch": a.arch, "classes": base.classes, "gray": a.gray,
                        "state_dict": model.state_dict()}, a.out)
            report = classification_report(ys, ps, labels=range(len(base.classes)),
                                           target_names=base.classes, digits=4, zero_division=0)
            with open(os.path.splitext(a.out)[0] + "_report.txt", "w") as f:
                f.write(f"{a.arch} {a.mode} gray={a.gray} train_ratio={a.train_ratio} "
                        f"best_acc={best:.4f}\n\n{report}")
    print(f"Done. Best test accuracy {best:.4f}. Saved to {a.out}")


if __name__ == "__main__":
    main()
