# from transformers import pipeline

# classifier = pipeline("token-classification", model = "bigcode/starpii", aggregation_strategy="simple")
# classifier("Hello I'm John and my IP address is 196.780.89.78")

# from transformers import AutoModelForTokenClassification, AutoTokenizer
# import torch

# # Load the pre-trained model and tokenizer
# model_name = "bigcode/starpii"
# model = AutoModelForTokenClassification.from_pretrained(model_name)
# tokenizer = AutoTokenizer.from_pretrained(model_name)

# # Prepare input text
# text = "from transformers import AutoModelForTokenClassification, AutoTokenizer import torch secretkey= cmVnrGtuOjAxOjE3MjEyODUwMjg6M0RrNjVMVGZEaGd6T0RiZ09FR3M5MEV5Tk0z ipadress= 10.83.73.87.84 email= abhi@gmail.com"
# inputs = tokenizer(text, return_tensors="pt")

# # Perform inference
# with torch.no_grad():
#     outputs = model(**inputs)

# # Get the predicted labels
# predicted_labels = torch.argmax(outputs.logits, dim=2)
# labels = [model.config.id2label[label_id] for label_id in predicted_labels[0].tolist()]

# # Print the labels
# print(labels)

# from transformers import AutoModelForTokenClassification, AutoTokenizer
# import torch

# # Load the pre-trained model and tokenizer
# model_name = "bigcode/starpii"
# model = AutoModelForTokenClassification.from_pretrained(model_name)
# tokenizer = AutoTokenizer.from_pretrained(model_name)

# # Prepare input text
# text = "from transformers import AutoModelForTokenClassification, AutoTokenizer import torch secretkey= cmVnrGtuOjAxOjE3MjEyODUwMjg6M0RrNjVMVGZEaGd6T0RiZ09FR3M5MEV5Tk0z ipadress= 10.83.73.87.84 email= abhi@gmail.com"
# inputs = tokenizer(text, return_tensors="pt")

# # Perform inference
# with torch.no_grad():
#     outputs = model(**inputs)

# # Get the predicted labels
# predicted_labels = torch.argmax(outputs.logits, dim=2)
# labels = [model.config.id2label[label_id] for label_id in predicted_labels[0].tolist()]

# # Replace IP address with the label or "IP_ADDRESS"
# output_text = text
# current_ip = ""
# for token, label in zip(inputs["input_ids"][0], labels):
#     token_text = tokenizer.decode(token).strip()
#     if label == "B-EMAIL":
#         current_ip += token_text
#     if label == "I-EMAIL":
#         current_ip += token_text
#     elif current_ip:
#         output_text = output_text.replace(current_ip, "EMAILID")
#         current_ip = ""

# print("output text",output_text)


## SAVED THE MODEL LOCALLY USING THIS CODE
## USING THIS CODE TEH HUGGINGFACE MODEL IS SAVED LOCALLY AND USED IN BELOW CODE 
## FOR TEXT AS WELL AS FILE DETECTION
# from transformers import AutoModelForTokenClassification, AutoTokenizer

# # Load the pre-trained model and tokenizer
# model_name = "bigcode/starpii"
# model = AutoModelForTokenClassification.from_pretrained(model_name)
# tokenizer = AutoTokenizer.from_pretrained(model_name)

# # Specify the directory where you want to save the model
# local_model_directory = "./nermodel"

# # Save the model and tokenizer to the local directory
# model.save_pretrained(local_model_directory)
# tokenizer.save_pretrained(local_model_directory)

# print(f"Model and tokenizer saved to {local_model_directory}")

## ABOVE COMMENTED CODE IS FOR REMOVAL!!!

# NER MODEL DETECTION FOR TEXT
from transformers import AutoModelForTokenClassification, AutoTokenizer
from privacy.config.logger import CustomLogger
import torch
import os
import autopep8

log = CustomLogger()

class code_detect_ner:
    def textner(text):
        # Load the model and tokenizer from the local directory
        log.info("Entering in textner function")
        local_model_directory = "privacy/util/code_detect/ner/pii_inference/nermodel"
        model = AutoModelForTokenClassification.from_pretrained(local_model_directory)
        tokenizer = AutoTokenizer.from_pretrained(local_model_directory)
        print("textNER", text)

        # Prepare input text
        inputs = tokenizer(text, return_tensors="pt")

        # Perform inference
        with torch.no_grad():
            outputs = model(**inputs)

        # Get the predicted labels
        predicted_labels = torch.argmax(outputs.logits, dim=2)
        labels = [model.config.id2label[label_id] for label_id in predicted_labels[0].tolist()]

        # Define a mapping of entity types to placeholders
        entity_mapping = {
            "NAME": "<NAME>",
            "EMAIL": "<EMAIL>",
            "IP_ADDRESS": "<IP_ADDRESS>",
            "KEY": "<KEY>",
        }

       # Initialize variables
        redacted_text = ""
        current_entity = None
        last_token_was_special = False

        # Redact entities in the original text
        for token, label in zip(tokenizer.convert_ids_to_tokens(inputs["input_ids"][0]), labels):
            if token.startswith("Ġ"):
                last_token_was_special = True
                token = token[1:]  # Remove the leading "Ġ" character
            else:
                last_token_was_special = False

            if label.startswith("B-"):
                current_entity = label[2:]
                redacted_text += f"<{entity_mapping.get(current_entity, current_entity)}>"
            elif label.startswith("I-") and current_entity is not None:
                pass  # Skip intermediate tokens of the entity
            else:
                current_entity = None
                if last_token_was_special and not token.startswith("Ġ"):
                    redacted_text += " "
                redacted_text += token

        # Print the redacted text
        #code_detect_ner.filener("privacy/util/code_detect/ner/pii_inference/input_code.java")
        print("Redacted Text:", redacted_text.strip())
        log.info("Returning from textner function")
        return redacted_text

    # def filener(input_code_file):
    #     ## NER DETECTION FROM FILE BUT FOR BIG CODE!!!!!!!!!!!!!!
    #     from transformers import AutoModelForTokenClassification, AutoTokenizer
    #     import torch

    #     # Load the model and tokenizer from the local directory
    #     local_model_directory = "privacy/util/code_detect/ner/pii_inference/nermodel"
    #     model = AutoModelForTokenClassification.from_pretrained(local_model_directory)
    #     tokenizer = AutoTokenizer.from_pretrained(local_model_directory, model_max_length=10000)

    #     # Specify the input code file
    #     #input_code_file = "input_code.java"
    #     # input_code_file = "input.py"

    #     # Read the code from the file
    #     with open(input_code_file, "r", encoding="utf-8") as file:
    #         code = file.read()
    #     #code = input_code_file.file.read()

    #     # Define a chunk size (adjust as needed)
    #     chunk_size = 1000

    #     # Initialize the redacted text
    #     redacted_text = ""
    #     current_entity = None
    #     last_token_was_special = False

    #     # Split the code into chunks
    #     code_chunks = [code[i:i + chunk_size] for i in range(0, len(code), chunk_size)]

    #     # Process each chunk
    #     for i, chunk in enumerate(code_chunks):
    #         # Prepare input text
    #         inputs = tokenizer(chunk, return_tensors="pt")

    #         # Perform inference
    #         with torch.no_grad():
    #             outputs = model(**inputs)

    #         # Get the predicted labels
    #         predicted_labels = torch.argmax(outputs.logits, dim=2)
    #         labels = [model.config.id2label[label_id] for label_id in predicted_labels[0].tolist()]

    #         # Define a mapping of entity types to placeholders
    #         entity_mapping = {
    #             "NAME": "<NAME>",
    #             "EMAIL": "<EMAIL>",
    #             "IP_ADDRESS": "<IP_ADDRESS>",
    #             
    #         }

    #         # Redact entities in the original text
    #         for token, label in zip(tokenizer.convert_ids_to_tokens(inputs["input_ids"][0]), labels):
    #             if token.startswith("Ġ"):
    #                 last_token_was_special = True
    #                 token = token[1:]  # Remove the leading "Ġ" character
    #             else:
    #                 last_token_was_special = False

    #             # Add space if the last token was a special token and the current token does not start with "<"
    #             if last_token_was_special and not token.startswith("<"):
    #                 redacted_text += " "

    #             if label.startswith("B-"):
    #                 current_entity = label[2:]
    #                 redacted_text += f"{entity_mapping.get(current_entity, current_entity)}"
    #             elif label.startswith("I-") and current_entity is not None:
    #                 pass  # Skip intermediate tokens of the entity
    #             else:
    #                 current_entity = None
    #                 redacted_text += token

    #     # Split the redacted text into lines and add indentation
    #     redacted_lines = redacted_text.split("Ċ")
    #     formatted_redacted_text = ""
    #     indentation = 0

    #     for line in redacted_lines:
    #         if "{" in line:
    #             formatted_redacted_text += "    " * indentation + line + "\n"
    #             indentation += 1
    #         elif "}" in line:
    #             indentation -= 1
    #             formatted_redacted_text += "    " * indentation + line + "\n"
    #         else:
    #             formatted_redacted_text += "    " * indentation + line + "\n"

    #     # Remove any remaining special characters
    #     formatted_redacted_text = formatted_redacted_text.replace("Ġ", "")

    #     # # Write the redacted code back to the file using UTF-8 encoding
    #     # output_code_file = "redacted_code.java"
    #     # with open(output_code_file, "a", encoding="utf-8") as file:
    #     #     file.write(formatted_redacted_text.strip())
    #     # Generate the output file name based on the input file name
    #     output_code_file = os.path.splitext(input_code_file)[0] + "_redacted" + os.path.splitext(input_code_file)[1]

    #     # Write the redacted code back to the file using UTF-8 encoding
    #     with open(output_code_file, "w", encoding="utf-8") as file:
    #         file.write(formatted_redacted_text.strip())
    #     # Delete the temporary input code file
    #     os.remove(input_code_file)
    #     # Print the final redacted text
    #     print("Redacted Text:", formatted_redacted_text.strip())
    #     return output_code_file





    # def filener(code_content, filename):
    #     # Load the model and tokenizer from the local directory
    #     local_model_directory = "privacy/util/code_detect/ner/pii_inference/nermodel"
    #     model = AutoModelForTokenClassification.from_pretrained(local_model_directory)
    #     tokenizer = AutoTokenizer.from_pretrained(local_model_directory, model_max_length=10000)

    #     # Define a chunk size (adjust as needed)
    #     chunk_size = 1000

    #     # Initialize the redacted text
    #     redacted_text = ""
    #     current_entity = None
    #     last_token_was_special = False

    #     # Split the code into chunks
    #     code_chunks = [code_content[i:i + chunk_size] for i in range(0, len(code_content), chunk_size)]

    #     # Process each chunk
    #     for i, chunk in enumerate(code_chunks):
    #         # Prepare input text
    #         chunk_str = chunk.decode("utf-8")
    #         inputs = tokenizer(chunk_str, return_tensors="pt")

    #         # Perform inference
    #         with torch.no_grad():
    #             outputs = model(**inputs)

    #         # Get the predicted labels
    #         predicted_labels = torch.argmax(outputs.logits, dim=2)
    #         labels = [model.config.id2label[label_id] for label_id in predicted_labels[0].tolist()]

    #         # Define a mapping of entity types to placeholders
    #         entity_mapping = {
    #             "NAME": "<NAME>",
    #             "EMAIL": "<EMAIL>",
    #             "IP_ADDRESS": "<IP_ADDRESS>",
    #             
    #         }

    #         # Redact entities in the original text
    #         for token, label in zip(tokenizer.convert_ids_to_tokens(inputs["input_ids"][0]), labels):
    #             if token.startswith("Ġ"):
    #                 last_token_was_special = True
    #                 token = token[1:]  # Remove the leading "Ġ" character
    #             else:
    #                 last_token_was_special = False

    #             # Add space if the last token was a special token and the current token does not start with "<"
    #             if last_token_was_special and not token.startswith("<"):
    #                 redacted_text += " "

    #             if label.startswith("B-"):
    #                 current_entity = label[2:]
    #                 redacted_text += f"{entity_mapping.get(current_entity, current_entity)}"
    #             elif label.startswith("I-") and current_entity is not None:
    #                 pass  # Skip intermediate tokens of the entity
    #             else:
    #                 current_entity = None
    #                 redacted_text += token

    #     # Split the redacted text into lines and add indentation
    #     redacted_lines = redacted_text.split("Ċ")
    #     formatted_redacted_text = ""
    #     indentation = 0
        
    #     for line in redacted_lines:
    #         if "{" in line:
    #             formatted_redacted_text += "    " * indentation + line + "\n"
    #             indentation += 1
    #         elif "}" in line:
    #             indentation -= 1
    #             formatted_redacted_text += "    " * indentation + line + "\n"
    #         else:
    #             formatted_redacted_text += "    " * indentation + line + "\n"

    #     # Remove any remaining special characters
    #     formatted_redacted_text = formatted_redacted_text.replace("Ġ", "")
    #     formatted_redacted_text = formatted_redacted_text.replace("č", "")
    #     print("formatted_redacted_text",formatted_redacted_text)
    #     # Generate the output file name based on the input file name
    #     output_code_file = os.path.splitext(filename)[0] + "_redacted" + os.path.splitext(filename)[1]

    #     # Write the redacted code back to the file using UTF-8 encoding
    #     with open(output_code_file, "w", encoding="utf-8") as file:
    #         file.write(formatted_redacted_text.strip())

    #     # Return the redacted text and the output code file name
    #     return formatted_redacted_text.strip().encode("utf-8"), output_code_file
    

    

    # def filener(code_content, filename):
    #     # Load the model and tokenizer from the local directory
    #     local_model_directory = "privacy/util/code_detect/ner/pii_inference/nermodel"
    #     model = AutoModelForTokenClassification.from_pretrained(local_model_directory)
    #     tokenizer = AutoTokenizer.from_pretrained(local_model_directory, model_max_length=10000)

    #     # Define a chunk size (adjust as needed)
    #     chunk_size = 1000

    #     # Initialize the redacted text
    #     redacted_text = ""
    #     current_entity = None
    #     last_token_was_special = False

    #     # Split the code into chunks
    #     code_chunks = [code_content[i:i + chunk_size] for i in range(0, len(code_content), chunk_size)]

    #     # Process each chunk
    #     for i, chunk in enumerate(code_chunks):
    #         # Prepare input text
    #         chunk_str = chunk.decode("utf-8")
    #         inputs = tokenizer(chunk_str, return_tensors="pt")

    #         # Perform inference
    #         with torch.no_grad():
    #             outputs = model(**inputs)

    #         # Get the predicted labels
    #         predicted_labels = torch.argmax(outputs.logits, dim=2)
    #         labels = [model.config.id2label[label_id] for label_id in predicted_labels[0].tolist()]

    #         # Define a mapping of entity types to placeholders
    #         entity_mapping = {
    #             "NAME": "<NAME>",
    #             "EMAIL": "<EMAIL>",
    #             "IP_ADDRESS": "<IP_ADDRESS>",
    #             ]
    #         }

    #         # Redact entities in the original text
    #         for token, label in zip(tokenizer.convert_ids_to_tokens(inputs["input_ids"][0]), labels):
    #             if token.startswith("Ġ"):
    #                 last_token_was_special = True
    #                 token = token[1:]  # Remove the leading "Ġ" character
    #             else:
    #                 last_token_was_special = False

    #             # Add space if the last token was a special token and the current token does not start with "<"
    #             if last_token_was_special and not token.startswith("<"):
    #                 redacted_text += " "

    #             if label.startswith("B-"):
    #                 current_entity = label[2:]
    #                 redacted_text += f"{entity_mapping.get(current_entity, current_entity)}"
    #             elif label.startswith("I-") and current_entity is not None:
    #                 pass  # Skip intermediate tokens of the entity
    #             else:
    #                 current_entity = None
    #                 redacted_text += token

    #     # Split the redacted text into lines and add indentation
    #     redacted_lines = redacted_text.split("Ċ")
    #     formatted_redacted_text = ""
    #     indentation = 0

    #     for line in redacted_lines:
    #         line = line.strip()

    #         if line.startswith(" "):
    #             formatted_line = "    " * indentation + line + "\n"
    #         elif line.startswith("#"):
    #             formatted_line = "    " * indentation + line + "\n"
    #         else:
    #             formatted_line = line + "\n"

    #         # Adjust indentation based on braces
    #         if "{" in line:
    #             indentation += 1
    #         elif "}" in line:
    #             indentation = max(0, indentation - 1)

    #         formatted_redacted_text += formatted_line

    #     # Remove any remaining special characters
    #     formatted_redacted_text = formatted_redacted_text.replace("Ġ", "")
    #     formatted_redacted_text = formatted_redacted_text.replace("č", "")

    #     # Generate the output file name based on the input file name
    #     output_code_file = os.path.splitext(filename)[0] + "_redacted" + os.path.splitext(filename)[1]

    #     # Write the formatted redacted code back to the file using UTF-8 encoding
    #     with open(output_code_file, "w", encoding="utf-8") as file:
    #         file.write(formatted_redacted_text.strip())

    #     # Use autopep8 to format the code in-place
    #     with open(output_code_file, "r", encoding="utf-8") as file:
    #         code_content = file.read()

    #     formatted_code = autopep8.fix_code(
    #         code_content,
    #         options={
    #             'aggressive': 1,
    #             'max_line_length': 120,  # Adjust this based on your desired line length
    #         }
    #     )

    #     # Write the formatted code back
    #     with open(output_code_file, "w", encoding="utf-8") as file:
    #         file.write(formatted_code)
            
    #     print("FORMCODE","\n",formatted_code)
    #     # Return the redacted text and the output code file name
    #     return formatted_code.encode("utf-8"), output_code_file
    
    def filener(code_content, filename):
        # Load the model and tokenizer from the local directory
        local_model_directory = "privacy/util/code_detect/ner/pii_inference/nermodel"
        model = AutoModelForTokenClassification.from_pretrained(local_model_directory)
        tokenizer = AutoTokenizer.from_pretrained(local_model_directory, model_max_length=10000)

        # Define a chunk size (adjust as needed)
        chunk_size = 1000

        # Initialize the redacted text
        redacted_text = ""
        current_entity = None
        last_token_was_special = False

        # Split the code into chunks
        code_chunks = [code_content[i:i + chunk_size] for i in range(0, len(code_content), chunk_size)]

        # Process each chunk
        for i, chunk in enumerate(code_chunks):
            # Prepare input text
            chunk_str = chunk.decode("utf-8")
            inputs = tokenizer(chunk_str, return_tensors="pt")

            # Perform inference
            with torch.no_grad():
                outputs = model(**inputs)

            # Get the predicted labels
            predicted_labels = torch.argmax(outputs.logits, dim=2)
            labels = [model.config.id2label[label_id] for label_id in predicted_labels[0].tolist()]

            # Define a mapping of entity types to placeholders
            entity_mapping = {
                "NAME": "<NAME>",
                "EMAIL": "<EMAIL>",
                "IP_ADDRESS": "<IP_ADDRESS>",
                "KEY": "<KEY>",
            }

            # Redact entities in the original text
            for token, label in zip(tokenizer.convert_ids_to_tokens(inputs["input_ids"][0]), labels):
                if token.startswith("Ġ"):
                    last_token_was_special = True
                    token = token[1:]  # Remove the leading "Ġ" character
                else:
                    last_token_was_special = False

                # Add space if the last token was a special token and the current token does not start with "<"
                if last_token_was_special and not token.startswith("<"):
                    redacted_text += " "

                if label.startswith("B-"):
                    current_entity = label[2:]
                    redacted_text += f"{entity_mapping.get(current_entity, current_entity)}"
                elif label.startswith("I-") and current_entity is not None:
                    pass  # Skip intermediate tokens of the entity
                else:
                    current_entity = None
                    redacted_text += token

        # Split the redacted text into lines and add indentation
        redacted_lines = redacted_text.split("Ċ")
        formatted_redacted_text = ""
        indentation = 0

        for line in redacted_lines:
            line = line.strip()

            if line.startswith(" "):
                formatted_line = "    " * indentation + line + "\n"
            elif line.startswith("#"):
                formatted_line = "    " * indentation + line + "\n"
            else:
                formatted_line = line + "\n"

            # Adjust indentation based on braces
            if "{" in line:
                indentation += 1
            elif "}" in line:
                indentation = max(0, indentation - 1)

            # Check if the line ends with a colon, indicating the start of a block
            if line.endswith(":"):
                indentation += 1

            formatted_redacted_text += formatted_line

        # Remove any remaining special characters
        formatted_redacted_text = formatted_redacted_text.replace("Ġ", "")
        formatted_redacted_text = formatted_redacted_text.replace("č", "")

        # Generate the output file name based on the input file name
        output_code_file = os.path.splitext(filename)[0] + "_redacted" + os.path.splitext(filename)[1]

        # Write the formatted redacted code back to the file using UTF-8 encoding
        with open(output_code_file, "w", encoding="utf-8") as file:
            file.write(formatted_redacted_text.strip())

        # Use autopep8 to format the code in-place
        with open(output_code_file, "r", encoding="utf-8") as file:
            code_content = file.read()

        formatted_code = autopep8.fix_code(
            code_content,
            options={
                'aggressive': 1,
                'max_line_length': 120,  # Adjust this based on your desired line length
            }
        )

        # Write the formatted code back
        with open(output_code_file, "w", encoding="utf-8") as file:
            file.write(formatted_code)
        print("FORMATTED CODE","\n", formatted_code)
        # Return the redacted text and the output code file name
        return formatted_code.encode("utf-8"), output_code_file












## FOR FILE WORKING
# from transformers import AutoModelForTokenClassification, AutoTokenizer
# import torch

# # Load the model and tokenizer from the local directory
# local_model_directory = "./nermodel"
# model = AutoModelForTokenClassification.from_pretrained(local_model_directory)
# tokenizer = AutoTokenizer.from_pretrained(local_model_directory,model_max_length=10000)

# # Specify the input code file
# input_code_file = "input_code.java"
# #input_code_file = "input.py"
# # Read the code from the file
# with open(input_code_file, "r", encoding="utf-8") as file:
#     code = file.read()

# # Prepare input text
# inputs = tokenizer(code, return_tensors="pt")
# # print("INPUT IDS",inputs["input_ids"].shape)
# # print("MODEL CONFIG",model.config)
# # print("TOKENIZER",tokenizer)
# # Perform inference
# with torch.no_grad():
#     outputs = model(**inputs)

# # Get the predicted labels
# predicted_labels = torch.argmax(outputs.logits, dim=2)
# labels = [model.config.id2label[label_id] for label_id in predicted_labels[0].tolist()]

# # Define a mapping of entity types to placeholders
# entity_mapping = {
#     "NAME": "<NAME>",
#     "EMAIL": "<EMAIL>",
#     "IP_ADDRESS": "<IP_ADDRESS>"
#     
# }

# # Initialize variables
# redacted_text = ""
# current_entity = None
# last_token_was_special = False

# # Redact entities in the original text
# for token, label in zip(tokenizer.convert_ids_to_tokens(inputs["input_ids"][0]), labels):
#     if token.startswith("Ġ"):
#         last_token_was_special = True
#         token = token[1:]  # Remove the leading "Ġ" character
#     else:
#         last_token_was_special = False

#     # Add space if the last token was a special token and the current token does not start with "<"
#     if last_token_was_special and not token.startswith("<"):
#         redacted_text += " "

#     if label.startswith("B-"):
#         current_entity = label[2:]
#         redacted_text += f"{entity_mapping.get(current_entity, current_entity)}"
#     elif label.startswith("I-") and current_entity is not None:
#         pass  # Skip intermediate tokens of the entity
#     else:
#         current_entity = None
#         redacted_text += token


# # Split the redacted text into lines and add indentation
# redacted_lines = redacted_text.split("Ċ")
# formatted_redacted_text = ""
# indentation = 0

# for line in redacted_lines:
#     if "{" in line:
#         formatted_redacted_text += "    " * indentation + line + "\n"
#         indentation += 1
#     elif "}" in line:
#         indentation -= 1
#         formatted_redacted_text += "    " * indentation + line + "\n"
#     else:
#         formatted_redacted_text += "    " * indentation + line + "\n"

# # Remove any remaining special characters
# formatted_redacted_text = formatted_redacted_text.replace("Ġ", "")

# # Write the redacted code back to the file using UTF-8 encoding
# output_code_file = "redacted_code.java"
# #output_code_file = "x.py"
# with open(output_code_file, "w", encoding="utf-8") as file:
#     file.write(formatted_redacted_text.strip())

# # Print the redacted text
# print("Redacted Text:", formatted_redacted_text.strip())








