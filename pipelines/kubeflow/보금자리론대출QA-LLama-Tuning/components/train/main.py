from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    AutoTokenizer,
    TrainingArguments,
)
from peft import LoraConfig
from trl import SFTTrainer, SFTConfig

import os
import torch

os.environ["NVIDIA_VISIBLE_DEVICES"] = "0"
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

print(torch.__version__)
print(torch.version.cuda)
print(torch.backends.cudnn.version())
print(torch.cuda.is_available())

dataset = load_dataset(
    "json", 
    data_files='sft_dataset.jsonl',
    split="train"
)

quant_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=False,
)

model = AutoModelForCausalLM.from_pretrained(
    "beomi/Llama-3-Open-Ko-8B",
    quantization_config=quant_config,
    device_map={"": 0}
)
model.config.use_cache = False
model.config.pretraining_tp = 1

tokenizer = AutoTokenizer.from_pretrained(
    "beomi/Llama-3-Open-Ko-8B",
    trust_remote_code=True
)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"

peft_params = LoraConfig(
    lora_alpha=16,
    lora_dropout=0.1,
    r=64,
    bias="none",
    task_type="CAUSAL_LM",
)

training_params = TrainingArguments(
    output_dir="/results",
    num_train_epochs=1,
    max_steps=5000,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=4,
    optim="paged_adamw_8bit",
    warmup_ratio=0.03,
    learning_rate=2e-4,
    fp16=True,
    logging_steps=100,
    push_to_hub=False,
    report_to='tensorboard',
)

training_args = SFTConfig(
    output_dir="./results",
    num_train_epochs=1,
    max_steps=5000,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=4,
    optim="paged_adamw_8bit",
    warmup_ratio=0.03,
    learning_rate=2e-4,
    bf16=True,  # fp16 대신 bf16 권장
    logging_steps=100,
    save_strategy="steps",
    save_steps=500,
    push_to_hub=False,
    # report_to='tensorboard',
    
    # SFT 전용 파라미터 (SFTConfig에서 직접 설정)
    max_length=256,
    packing=False,
    dataset_text_field="text",
)

trainer = SFTTrainer(
    model=model,
    args=training_args,  # SFTConfig 전달
    train_dataset=dataset,
    processing_class=tokenizer,  # tokenizer 대신 processing_class
    peft_config=peft_params,
    # dataset_text_field, max_seq_length, packing은 SFTConfig로 이동
)

trainer.train()