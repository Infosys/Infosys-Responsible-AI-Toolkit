import torch
from transformers import AutoModelForTokenClassification, AutoTokenizer
from utils import PiiNERPipeline
from datasets import Dataset
from pii_redaction.utils import redact_pii_batch, get_replacements
def main():
    model_path = "pii_inference/nermodel"
    code_file_path = "input_code.java"
    model = AutoModelForTokenClassification.from_pretrained(model_path)
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    pipeline = PiiNERPipeline(
        model,
        tokenizer=tokenizer,
        batch_size=1024,
        window_size=512,
        device=torch.device("cuda" if torch.cuda.is_available() else "cpu"),
        num_workers=0,
        id_to_label=model.config.id2label,
        window_overlap=False,
        bf16=True
    )
    with open(code_file_path, "r") as file:
        code = file.read()
    sentences = code.split(". ")
    print(sentences, "SENTENCES")
    ids = list(range(len(sentences)))
    dataset = Dataset.from_dict({"content": sentences, "id": ids})
    result = pipeline(dataset)
    replacements = get_replacements()
    results = list(result)
    print(results, "RESULT")
    redacted_results = redact_pii_batch(results, replacements)
    print(redacted_results, "redacted_results")

if __name__ == "__main__":
    main()
