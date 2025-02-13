from datasets import load_dataset
import soundfile as sf
import torch
from modeling.asr import SLAM_ASR


asr = SLAM_ASR(
    "facebook/hubert-base-ls960",
    "TinyLlama/TinyLlama-1.1B-Chat-v0.4",
    train_mode="adapter",
)
# load the state_dict from output/adapter_weights.pt
asr.load_state_dict(torch.load("output/adapter_weights.pt", weights_only=False), strict=False)


def map_to_array(batch):
    batch["speech"] = torch.tensor(batch["audio"]["array"], dtype=torch.float32)
    return batch


ds = load_dataset(
    "hf-internal-testing/librispeech_asr_dummy",
    "clean",
    split="validation",
    trust_remote_code=True,
    cache_dir="dataset_cache",
    download_mode="force_redownload"
)
ds = ds.map(map_to_array)

for i in range(len(ds)):
    x = ds["speech"][i]
    y = ds["text"][i]
    # asr(x)
    output = asr.generate(x)  # causal of shape (b, seq_len, vocab_size)
    print(f"Predicted: {asr.language_tokenizer.batch_decode(output)[0]}")
    print(f"Reference: {y.lower()}")
    print("\n\n")
