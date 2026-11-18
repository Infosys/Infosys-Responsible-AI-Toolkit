from transformers import AutoModelForTokenClassification, AutoTokenizer
import torch
import os
import autopep8
import re
USERNAME_PLACEHOLDER = "<USERNAME>"
EMAIL_PLACEHOLDER = "<EMAIL>"
IP_ADDRESS_PLACEHOLDER = "<IP_ADDRESS>"
KEY_PLACEHOLDER = "<KEY>"
NAME_PLACEHOLDER = "<NAME>"
class code_detect_ner:
    def textner(self,text):
        local_model_directory = "privacy/util/code_detect/ner/pii_inference/nermodel"
        model = AutoModelForTokenClassification.from_pretrained(local_model_directory)
        tokenizer = AutoTokenizer.from_pretrained(local_model_directory)
        print("textNER", text)
        inputs = tokenizer(text, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**inputs)
        predicted_labels = torch.argmax(outputs.logits, dim=2)
        labels = [model.config.id2label[label_id] for label_id in predicted_labels[0].tolist()]
        print(predicted_labels,"predicted_labels")
        print("labels",labels)
        entity_mapping = {
            USERNAME_PLACEHOLDER: USERNAME_PLACEHOLDER,
            EMAIL_PLACEHOLDER: EMAIL_PLACEHOLDER,
            IP_ADDRESS_PLACEHOLDER: IP_ADDRESS_PLACEHOLDER,
            KEY_PLACEHOLDER: KEY_PLACEHOLDER,
            }
        redacted_text = ""
        current_entity = None
        last_token_was_special = False
        for token, label in zip(tokenizer.convert_ids_to_tokens(inputs["input_ids"][0]), labels):
            if token.startswith("Ġ"):
                last_token_was_special = True
                token = token[1:] 
            else:
                last_token_was_special = False

            if label.startswith("B-"):
                current_entity = label[2:]
                redacted_text += f"<{entity_mapping.get(current_entity, current_entity)}>"
            elif label.startswith("I-") and current_entity is not None:
                pass  
            else:
                current_entity = None
                if last_token_was_special and not token.startswith("Ġ"):
                    redacted_text += " "
                redacted_text += token
        redacted_text = redacted_text.replace("Ġ", "")
        redacted_text = redacted_text.replace("č", "")
        redacted_text = redacted_text.replace("Ċ", "")
        print("Redacted Text:", redacted_text.strip())
        return redacted_text

    
    def filener(self,code_content, filename,model,tokenizer):
        chunk_size = 1000
        redacted_text = ""
        current_entity = None
        last_token_was_special = False
        code_chunks = [code_content[i:i + chunk_size] for i in range(0, len(code_content), chunk_size)]
        for i, chunk in enumerate(code_chunks):
            chunk_str = chunk.decode("utf-8")
            inputs = tokenizer(chunk_str, return_tensors="pt")
            with torch.no_grad():
                outputs = model(**inputs)
            predicted_labels = torch.argmax(outputs.logits, dim=2)
            labels = [model.config.id2label[label_id] for label_id in predicted_labels[0].tolist()]
            entity_mapping = {
                "USERNAME": USERNAME_PLACEHOLDER,
                "EMAIL": EMAIL_PLACEHOLDER,
                "IP_ADDRESS": IP_ADDRESS_PLACEHOLDER,
                "KEY": KEY_PLACEHOLDER,
                "NAME": NAME_PLACEHOLDER
            }

            for token, label in zip(tokenizer.convert_ids_to_tokens(inputs["input_ids"][0]), labels):
                if token.startswith("Ġ"):
                    last_token_was_special = True
                    token = token[1:]  
                else:
                    last_token_was_special = False
                if last_token_was_special and not token.startswith("<"):
                    redacted_text += " "

                if label.startswith("B-"):
                    current_entity = label[2:]
                    redacted_text += f"{entity_mapping.get(current_entity, current_entity)}"
                elif label.startswith("I-") and current_entity is not None:
                    pass  
                else:
                    current_entity = None
                    redacted_text += token

        redacted_lines = redacted_text.split("Ċ")
        formatted_redacted_text = ""
        indentation = 0

        for line in redacted_lines:
            print("line--",line +"\n")
            line = line.strip()

            if line.startswith(" "):
                formatted_line = "  " * indentation + line + "\n"
            elif line.startswith('Ġ'):
                formatted_line = " " + line + "\n"
            elif line.startswith('ĉ'):
                formatted_line = "        " + line + "\n"
            elif line.startswith("#"):
                formatted_line = "    " * indentation + line + "\n"    
            else:
                formatted_line = " " + line + "\n"
            print("--formatted line--",formatted_line)
            if "{" in line:
                indentation += 1
            elif "}" in line:
                indentation = max(0, indentation - 1)

           
            if line.endswith(":"):
                indentation += 1

            formatted_redacted_text += formatted_line
        
        formatted_redacted_text = formatted_redacted_text.replace("Ġ", " ")
        print("to be removed chars--",formatted_redacted_text)

        formatted_redacted_text = formatted_redacted_text.replace("č", " ")
        formatted_redacted_text = formatted_redacted_text.replace("ĉ", " ") 
        redacted_text = formatted_redacted_text.replace("Ċ", " ")
        output_code_file = os.path.splitext(filename)[0] + "_redacted" + os.path.splitext(filename)[1]

        with open(output_code_file, "w", encoding="utf-8") as file:
            file.write(formatted_redacted_text.strip())

        with open(output_code_file, "r", encoding="utf-8") as file:
            code_content = file.read()

        formatted_code = autopep8.fix_code(
            code_content,
            options={
                'aggressive': 1,
                'max_line_length': 120,  
            }
        )

 
        with open(output_code_file, "w", encoding="utf-8") as file:
            file.write(formatted_code)
        return formatted_code.encode("utf-8"), output_code_file