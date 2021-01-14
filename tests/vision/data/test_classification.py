from imp import reload
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest
import torch
import torchvision.transforms as T
from PIL import Image

from pl_flash.vision import ImageClassificationData


def _dummy_image_loader(filepath):
    return torch.rand(3, 64, 64)


def _rand_image():
    return Image.fromarray(np.random.randint(0, 255, (64, 64, 3), dtype="uint8"))


def test_from_filepaths(tmpdir):
    img_data = ImageClassificationData.from_filepaths(
        train_filepaths=["a", "b"],
        train_labels=[0, 1],
        train_transform=lambda x: x,  # make sure transform works
        loader=_dummy_image_loader,
        batch_size=1,
        num_workers=0,
    )

    data = next(iter(img_data.train_dataloader()))
    imgs, labels = data
    assert imgs.shape == (1, 3, 64, 64)
    assert labels.shape == (1,)

    assert img_data.val_dataloader() is None
    assert img_data.test_dataloader() is None

    img_data = ImageClassificationData.from_filepaths(
        train_filepaths=["a", "b"],
        train_labels=[0, 1],
        train_transform=None,
        valid_filepaths=["c", "d"],
        valid_labels=[0, 1],
        valid_transform=None,
        test_filepaths=["e", "f"],
        test_labels=[0, 1],
        loader=_dummy_image_loader,
        batch_size=1,
        num_workers=0,
    )

    data = next(iter(img_data.val_dataloader()))
    imgs, labels = data
    assert imgs.shape == (1, 3, 64, 64)
    assert labels.shape == (1,)

    data = next(iter(img_data.test_dataloader()))
    imgs, labels = data
    assert imgs.shape == (1, 3, 64, 64)
    assert labels.shape == (1,)


def test_from_folders(tmpdir):
    train_dir = Path(tmpdir / "train")
    train_dir.mkdir()

    (train_dir / "a").mkdir()
    _rand_image().save(train_dir / "a" / "1.png")
    _rand_image().save(train_dir / "a" / "2.png")

    (train_dir / "b").mkdir()
    _rand_image().save(train_dir / "b" / "1.png")
    _rand_image().save(train_dir / "b" / "2.png")

    img_data = ImageClassificationData.from_folders(
        train_dir, train_transform=None, loader=_dummy_image_loader, batch_size=1
    )
    data = next(iter(img_data.train_dataloader()))
    imgs, labels = data
    assert imgs.shape == (1, 3, 64, 64)
    assert labels.shape == (1,)

    assert img_data.val_dataloader() is None
    assert img_data.test_dataloader() is None

    img_data = ImageClassificationData.from_folders(
        train_dir,
        train_transform=T.ToTensor(),
        valid_folder=train_dir,
        valid_transform=T.ToTensor(),
        test_folder=train_dir,
        batch_size=1,
        num_workers=0,
    )

    data = next(iter(img_data.val_dataloader()))
    imgs, labels = data
    assert imgs.shape == (1, 3, 64, 64)
    assert labels.shape == (1,)

    data = next(iter(img_data.test_dataloader()))
    imgs, labels = data
    assert imgs.shape == (1, 3, 64, 64)
    assert labels.shape == (1,)