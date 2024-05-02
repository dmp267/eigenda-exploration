import os, sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from zarr_utils import get_dataset_bytes


dataset = "agb-quarterly"

cid, data_bytes = get_dataset_bytes(dataset)
print(f'CID: {cid}')
print(f'Data Bytes length: {len(data_bytes)}')