from huggingface_hub import snapshot_download
import os

snapshot_download(
    repo_id="beomi/gemma-ko-2b",
    local_dir="/home/ec2-user/models/",
    token=os.environ.get('HF_TOKEN'),
    local_dir_use_symlinks=False,
    ignore_patterns=["original/*"],
)
