"""Here we detect PII: Emails, IP addresses, and keys (SSH/API) and redact/anonymize them
    * we use one regex for emails and one for IP addresses
    * for keys we use detect-secrets tool, which is a combination of multiple plugins (regexes, entropy..)
    * we also add some filters on top of each tool to decrease the number of false positives
This script is adapted from https://github.com/bigscience-workshop/data-preparation/blob/main/preprocessing/training/02_pii/pii_processor.py
"""

import argparse
import random
import json
import logging
from pprint import pformat
from functools import partial

from datasets.utils.logging import set_verbosity_info
from datasets import load_dataset

from pii_detection import scan_pii_batch
from pii_redaction import redact_pii_batch, random_replacements
from utils.manual_sharding import save_manual_shards

def parse_args():
    parser = argparse.ArgumentParser(description="PII detection and redaction")
    parser.add_argument(
        "--dataset_name",
        default="bigcode/pii-for-code",
        type=str,
        help="HF repo name/path of the dataset.",
    )
    parser.add_argument(
        "--subset",
        default="data/",
        type=str,
        help="Data subset to use.",
    )
    parser.add_argument(
        "--text_column",
        default="content",
        type=str,
        help="Text column to use, if will be renamed to content",
    )
    parser.add_argument(
        "--split",
        default="train",
        type=str,
        help="Dataset split to process",
    )
    parser.add_argument(
        "--batch_size",
        default=100,
        type=int,
        help="Batch size for the PII detection/redaction",
    )
    parser.add_argument(
        "--seed",
        default=0,
        type=int,
        help="Seed for random",
    )
    parser.add_argument(
        "--num_proc",
        default=96,
        type=int,
        help="Number of processes to use for the PII detection/redaction",
    )
    parser.add_argument(
        "--no_redaction",
        action="store_true",
        help="If set, we don't perform redaction",
    )
    parser.add_argument(
        "--load_replacements",
        default=True,
        help="If set, we load the replacements from file replacements.json",
    )
    parser.add_argument(
        "--add_reference_text",
        default=True,
        type=bool,
        help="If True we add the reference text with PII between delimiters \
        in the redacted text -used for visualization-",
    )
    parser.add_argument(
        "--check_all_files",
        action="store_true",
        help="If set, we check all files, not only the ones that contain PII",
    )
    parser.add_argument(
        "--check_sampling_size",
        default=0,
        type=int,
        help="Number of samples to check for PII",
    )
    parser.add_argument(
        "--save_mode",
        default="manual_shards",
        type=str,
        choices=["hub", "local", "manual_shards"],
        help="How to save the dataset",
    )
    parser.add_argument(
        "--save_mode_checks",
        default="hub",
        type=str,
        choices=["hub", "local", "manual_shards"],
        help="How to save the  checks dataset",
    )
    parser.add_argument(
        "--target_dataset",
        default="bigcode-pii-pjj",
        type=str,
        help="HF repo name of the target dataset in save_mode=hub.",
    )
    parser.add_argument(
        "--hub_username",
        default="loubnabnl",
        type=str,
        help="Username for the hub",
    )
    parser.add_argument(
        "--save_path_disk",
        default="bigcode-pii-pjj-local",
        type=str,
        help="Path to save the dataset on disk in save_mode=local.",
    )
    parser.add_argument(
        "--remove_columns_the_stack",
        default=True,
        type=bool,
        help="The Stack v1.1 has many columns and this can cause an issue during processing of large subsets.",
    )
    return parser.parse_args()


def get_check_ds(ds, args):
    if not args.check_all_files:
        ds_checks = ds.filter(
            lambda exs: exs["modified"],
            batched=True,
            batch_size=args.batch_size,
            num_proc=args.num_proc
        )
    else:
        ds_checks = ds
    if not args.check_sampling_size:
        sampling_size = len(ds_checks)
    idx_samples = random.sample(range(len(ds_checks)), min(len(ds_checks), sampling_size))
    ds_checks = ds_checks.select(idx_samples)

    return ds_checks


def main():
    set_verbosity_info()
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S",
        level=logging.INFO,
        handlers=[
        logging.FileHandler("pii.log"),
        logging.StreamHandler()
    ]
    )
    args = parseArgs()
    logger.info(f"** The job is running with the following arguments: **\n{args}\n **** ")

    logger.info(f" ===== Loading {args.dataset_name} =====")
    ds = load_dataset(args.dataset_name, data_dir=args.subset, split=args.split, use_auth_token=True)
    if args.text_column != "content":
        ds = ds.rename_column(args.text_column, "content")
    
    logger.info(" ===== Adding an index column =====")
    ds = ds.add_column("index", list(range(len(ds))))

    logger.info(" ===== Applying PII detection =====")
    ds_pii = ds.map(
        scan_pii_batch, batched=True, batch_size=args.batch_size, num_proc=args.num_proc, load_from_cache_file=False
    )
    logger.info("Dataset info after PII detection:\n{ds_pii}")
    logger.info("Number of samples that contained PII: {sum(ds_pii['has_secrets'])}")
    logger.info("Total number of secrets found: {sum(ds_pii['number_secrets'])}")

    
    if not args.no_redaction:
        logger.info(" ===== Applying PII redaction =====")
        random.seed(args.seed)

        
        if args.load_replacements:
            with open("replacements.json", "r") as f:
                replacements = json.load(f)
        else:
            replacements = random_replacements()
            with open("random_replacements.json", "w") as f:
                json.dump(replacements, f)
        logging.info(f"Using the following replacements:\n{pformat(replacements)}")
        ds_pii = ds_pii.map(
            partial(redact_pii_batch, replacements=replacements, add_references=args.add_reference_text),
            batched=True,
            batch_size=args.batch_size,
            num_proc=args.num_proc,
            load_from_cache_file=False
        )
        logging.info("Dataset info after PII redaction:\n{ds_pii}")

        
        logger.info(" ===== Checking {args.check_sampling_size} samples from those modified in the dataset =====")

       
        

            
            
            
        logger.info("Removing columns that are not needed for the final dataset")
        columns = ["content", "modified", "secrets", "has_secrets", "number_secrets"]
        if args.add_reference_text:
            columns.append("references")
        ds_pii = ds_pii.remove_columns(columns) 
        ds_pii = ds_pii.rename_column("new_content", "content")
        logger.info("Dataset info after removing columns:\n{ds_pii}")
        logger.info(" ===== Saving the dataset to disk as JSON =====")
        ds_pii_df = ds_pii.to_pandas()
        ds_pii_df.to_json(args.save_path_disk + ".json", orient='records', lines=True)
    
   
    if args.save_mode == "hub":
        logger.info(" ===== Pushing the dataset to the Hub as: {args.target_dataset} =====")
        ds_pii.push_to_hub(args.target_dataset)

    
    elif args.save_mode == "local":
        logger.info(" ===== Saving the dataset to disk as JSON =====")
        ds_pii_df = ds_pii.to_pandas()
        ds_pii_df.to_json(args.save_path_disk + ".json", orient='records', lines=True)

    elif args.save_mode == "manual_shards":
        logger.info(" ===== Saving the dataset in manual shards =====")
        save_manual_shards(ds_pii, user=args.hub_username, remote_dataset_repo=args.target_dataset)
    
    logger.info(" ===== Dataset saved successfully =====")

if __name__ == "__main__":
    main()
