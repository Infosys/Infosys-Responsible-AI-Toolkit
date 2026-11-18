import torch
from transformers import AutoModelForTokenClassification, AutoTokenizer
from datasets import Dataset

from privacy.util.code_detect.ner.pii_redaction.utils import get_replacements, redact_pii_batch
import json
import re
import os
import re
from privacy.util.code_detect.ner.pii_inference.utils.pipeline import PiiNERPipeline
class CodeNer:
    @staticmethod
    def code_file(code, filename, model, tokenizer):
        if isinstance(code, bytes):
            code = code.decode('utf-8')
        print(code, "CODE")
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

        sentences = re.split('(?<=\. )(?!$|[a-z])', code)
        print(sentences, "############SENTENCES#########")
        ids = list(range(len(sentences)))
        dataset = Dataset.from_dict({"content": sentences, "id": ids})

        replacements = get_replacements()
        result = pipeline(dataset)

        results = list(result)
        print(results, "RESULT")

        examples = {
            "content": [res["content"] for res in results],
            "entities": [res["entities"] for res in results]
        }

      
        redacted_results = redact_pii_batch(examples, replacements)
        print(redacted_results, "redacted_code_parts")

        redacted_code_parts = redacted_results["new_content"]
        print(redacted_code_parts, "redacted_code_parts")
       
        output_code_file = os.path.splitext(filename)[0] + "_redacted" + os.path.splitext(filename)[1]
        try:
           
            with open(output_code_file, "w") as file:
                content = ''.join(redacted_code_parts)
               
                file.write(content)
                print(content, "content")    
        except Exception :
            print(f"An error occurred while writing to the file")
            
        return content, output_code_file
    @staticmethod
    def code_text(code, model, tokenizer):

        if isinstance(code, bytes):
            code = code.decode('utf-8')

        try:

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

            lines = code.split('\n')

            sentences = []

            for line in lines:
                if line.strip():
                    leading_spaces = len(line) - len(line.lstrip())
                   
                    sentences.append(' ' * leading_spaces + line.strip())
                else:    
                    sentences.append(' ')
            
          
            ids = list(range(len(sentences)))

            
            dataset = Dataset.from_dict({"content": sentences, "id": ids})

            replacements = get_replacements()

          
            result = pipeline(dataset)

          
            results = list(result)

        
            examples = {
                "content": [res["content"] for res in results],
                "entities": [res["entities"] for res in results]
            }

          
            redacted_results = redact_pii_batch(examples, replacements)

    
            redacted_code_parts = redacted_results["new_content"]

            redacted_code = '\n'.join(redacted_code_parts)

            redacted_response = re.sub(r'\n\s*\n', '\n\n', redacted_code)

            return redacted_response

        except Exception as e:
            print(f"An error occurred during processing: {e}")
            return None
