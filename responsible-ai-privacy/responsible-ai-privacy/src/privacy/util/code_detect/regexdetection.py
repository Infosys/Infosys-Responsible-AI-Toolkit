import json
import logging
import random
import os
import secrets
from privacy.util.code_detect.pii_detection import scan_pii_batch
from privacy.util.code_detect.pii_redaction import redact_pii_batch, random_replacements
class code_detect:

    def code_detect_regex(self,input_code_text):
        #output_file
        seed=0 
        no_redaction=False
        load_replacements=True 
        add_reference_text=True
        logging.basicConfig(format="%(asctime)s - %(levelname)s - %(name)s - %(message)s", level=logging.INFO)
        # Apply PII detection
        ds_pii = scan_pii_batch([{"content": input_code_text}])

        logging.info("PII detection results:\n{ds_pii}")
        logging.info("Number of samples that contained PII: {sum(ds_pii['has_secrets'])}")
        logging.info("Total number of secrets found: {sum(ds_pii['number_secrets'])}")

        # Redact PII in the code
        if not no_redaction:
            logging.info(" ===== Applying PII redaction =====")
            secrets.choice(seed)

            # Use random replacements by default
            replacements=None
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
            logging.info("Using the following replacements:\n{replacements}")

            ds_pii_redacted = redact_pii_batch(
                [{"content": input_code_text, "secrets": ds_pii['secrets'], "has_secrets": ds_pii['has_secrets'],
                "number_secrets": ds_pii['number_secrets']}],
                replacements=replacements,
                add_references=add_reference_text
            )

            redacted_code = ds_pii_redacted["new_content"][0]  # Access the redacted code
            print("Redacted Code:")
            logging.info("Redacted code saved successfully.")
            return redacted_code

    
