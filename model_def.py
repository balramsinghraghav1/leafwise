"""Shared model definition (AlexNet / GoogLeNet) used by train.py and app."""
import torch.nn as nn
from torchvision import models

MEAN = [0.485, 0.456, 0.406]
STD = [0.229, 0.224, 0.225]
ARCHS = ("alexnet", "googlenet")


def build_model(arch: str, n_classes: int, pretrained: bool):
    if arch == "alexnet":
        m = models.alexnet(weights=models.AlexNet_Weights.DEFAULT if pretrained else None)
        m.classifier[6] = nn.Linear(4096, n_classes)
    elif arch == "googlenet":
        if pretrained:
            m = models.googlenet(weights=models.GoogLeNet_Weights.DEFAULT)
        else:
            m = models.googlenet(weights=None, aux_logits=False, init_weights=False,
                                 transform_input=True)
        # drop auxiliary heads so forward() always returns a plain tensor
        m.aux_logits = False
        m.aux1 = None
        m.aux2 = None
        m.fc = nn.Linear(1024, n_classes)
    else:
        raise ValueError(f"arch must be one of {ARCHS}")
    return m
