import json
import torch
from albumentations.pytorch import ToTensorV2
from datasets import SegDataset
from models import SegModel
from utils import mask_to_rle

def main():
    
    model = SegModel.load_from_checkpoint("checkpoints/epoch=4-val_loss=0.45-val_high_vegetation_IoU=65.14-val_mIoU=66.81.ckpt")
    
    ds = SegDataset(phase="warmup", split="valid", transform=ToTensorV2())
    model.eval()
    results = {}
    for i, batch in enumerate(ds):
        filename = ds.img_list[i]
        img, _ = batch
        out = model(img.float().unsqueeze(dim=0).to(model.device))['out']
        probs = torch.softmax(out, dim=1)
        pred = torch.argmax(probs, dim=1)
        pred = pred.detach().cpu().numpy().squeeze()

        rle = mask_to_rle(pred)
        results[filename] = {
            "counts": rle,
            "height": pred.shape[0],
            "width": pred.shape[1],
        }
    
    with open("results.json", "w") as f:
        json.dump(results, f)


if __name__ == "__main__":
    main()