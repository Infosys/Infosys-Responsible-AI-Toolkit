
## REGEX FOR FILE
# import argparse
# import json
# import logging
# import random

# from pii_detection import scan_pii_batch
# from pii_redaction import redact_pii_batch, random_replacements

# def parse_args():
#     parser = argparse.ArgumentParser(description="PII detection and redaction for a code file")
#     parser.add_argument(
#         "--input_code_file",
#         required=True,
#         type=str,
#         help="Path to the input code file for PII detection and redaction",
#     )
#     parser.add_argument(
#         "--output_file",
#         required=True,
#         type=str,
#         help="Path to save the redacted code file",
#     )
#     parser.add_argument(
#         "--batch_size",
#         default=8,
#         type=int,
#         help="Batch size for the PII detection/redaction",
#     )
#     parser.add_argument(
#         "--seed",
#         default=0,
#         type=int,
#         help="Seed for random",
#     )
#     parser.add_argument(
#         "--num_proc",
#         default=8,
#         type=int,
#         help="Number of processes to use for PII detection/redaction",
#     )
#     parser.add_argument(
#         "--no_redaction",
#         action="store_true",
#         help="If set, do not perform redaction",
#     )
#     parser.add_argument(
#         "--load_replacements",
#         default=True,
#         help="If set, load replacements from file replacements.json",
#     )
#     parser.add_argument(
#         "--add_reference_text",
#         default=True,
#         type=bool,
#         help="If True, add reference text with PII between delimiters in the redacted text (used for visualization)",
#     )
#     return parser.parse_args()

# def main():
#     logging.basicConfig(format="%(asctime)s - %(levelname)s - %(name)s - %(message)s", level=logging.INFO)

#     args = parse_args()

#     # Read input code file
#     with open(args.input_code_file, "r") as input_file:
#         code_content = input_file.read()

#     # Apply PII detection
#     ds_pii = scan_pii_batch([{"content": code_content}])

#     logging.info(f"PII detection results:\n{ds_pii}")
#     logging.info(f"Number of samples that contained PII: {sum(ds_pii['has_secrets'])}")
#     logging.info(f"Total number of secrets found: {sum(ds_pii['number_secrets'])}")

#     # Redact PII in the code
#     if not args.no_redaction:
#         logging.info(f" ===== Applying PII redaction =====")
#         random.seed(args.seed)

#         # Use random replacements by default
#         if args.load_replacements:
#             with open("replacements.json", "r") as f:
#                 replacements = json.load(f)
#         else:
#             replacements = random_replacements()
#             with open("random_replacements.json", "w") as f:
#                 json.dump(replacements, f)
#         logging.info(f"Using the following replacements:\n{replacements}")

#         ds_pii_redacted = redact_pii_batch(
#             [{"content": code_content, "secrets": ds_pii['secrets'], "has_secrets": ds_pii['has_secrets'], "number_secrets": ds_pii['number_secrets']}],
#             replacements=replacements,
#             add_references=args.add_reference_text
#         )

#         redacted_code = ds_pii_redacted["new_content"][0]  # Access the redacted code
#         print("Redacted Code:")
#         print(redacted_code)

#         # Save the redacted code to the output file
#         with open(args.output_file, "w") as output_file:
#             output_file.write(redacted_code[0] if isinstance(redacted_code, list) else redacted_code)

#         logging.info("Redacted code saved successfully.")

# if __name__ == "__main__":
#     main()



#REGEX AS For text DETECTION
import json
import logging
import random
import os
import secrets
from privacy.util.code_detect.pii_detection import scan_pii_batch
from privacy.util.code_detect.pii_redaction import redact_pii_batch, random_replacements
class code_detect:

    def codeDetectRegex(input_code_text):
        #output_file
        batch_size=8
        seed=0 
        num_proc=8 
        no_redaction=False
        load_replacements=True 
        add_reference_text=True
        logging.basicConfig(format="%(asctime)s - %(levelname)s - %(name)s - %(message)s", level=logging.INFO)
        print("input_code_text",input_code_text)
        # Apply PII detection
        ds_pii = scan_pii_batch([{"content": input_code_text}])

        logging.info(f"PII detection results:\n{ds_pii}")
        logging.info(f"Number of samples that contained PII: {sum(ds_pii['has_secrets'])}")
        logging.info(f"Total number of secrets found: {sum(ds_pii['number_secrets'])}")

        # Redact PII in the code
        if not no_redaction:
            logging.info(f" ===== Applying PII redaction =====")
            secrets.choice(seed)

            # Use random replacements by default
            if load_replacements:
                with open("privacy/util/code_detect/replacements.json", "r") as f:
                    replacements = json.load(f)
            else:
                # Get the path to the directory of the current script
                current_dir = os.path.dirname(os.path.abspath(__file__))
                replacements_file_path = os.path.join(current_dir, "privacy", "util", "code_detect", "replacements.json")
                replacements = random_replacements()
                with open(replacements_file_path, "w") as f:
                    json.dump(replacements, f)
            logging.info(f"Using the following replacements:\n{replacements}")

            ds_pii_redacted = redact_pii_batch(
                [{"content": input_code_text, "secrets": ds_pii['secrets'], "has_secrets": ds_pii['has_secrets'],
                "number_secrets": ds_pii['number_secrets']}],
                replacements=replacements,
                add_references=add_reference_text
            )

            redacted_code = ds_pii_redacted["new_content"][0]  # Access the redacted code
            print("Redacted Code:")
            print(redacted_code)

            # # Save the redacted code to the output file
            # with open(output_file, "w") as output_file:
            #     output_file.write(redacted_code[0] if isinstance(redacted_code, list) else redacted_code)

            logging.info("Redacted code saved successfully.")
            return redacted_code

    
