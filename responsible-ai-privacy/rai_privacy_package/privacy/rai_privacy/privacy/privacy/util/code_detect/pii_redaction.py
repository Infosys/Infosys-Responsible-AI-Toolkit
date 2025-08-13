import json
import random
import string
import ipaddress

# List of random private IP addresses to use as replacements
REPLACEMENTS_IP = {
    "IPv4": ["172.16.31.10", "172.16.58.3", "172.16.17.32", "192.168.127.12", "192.168.3.11"],
    "IPv6": [
        "fd00:c2b6:b24b:be67:2827:688d:e6a1:6a3b",
        "fd00:a516:7c1b:17cd:6d81:2137:bd2a:2c5b",
        "fc00:e968:6179::de52:7100",
        "fc00:db20:35b:7399::5",
        "fdf8:f53e:61e4::18",
    ],
}

POPULAR_DNS_SERVERS = [
    "8.8.8.8",
    "8.8.4.4",
    "1.1.1.1",
    "1.0.0.1",
    "76.76.19.19",
    "76.223.122.150",
    "9.9.9.9",
    "149.112.112.112",
    "208.67.222.222",
    "208.67.220.220",
    "8.26.56.26",
    "8.20.247.20",
    "94.140.14.14",
    "94.140.15.15",
]

def load_json(sample):
    try:
        loaded = json.loads(sample)
        if isinstance(loaded, list):
            return loaded
        else:
            raise ValueError("Invalid JSON structure")
    except (json.JSONDecodeError, TypeError, ValueError):
        return sample

def random_replacements(n=10):
    letters = string.ascii_lowercase
    letters_digits = string.ascii_lowercase + string.digits
    emails = ["".join(random.choice(letters) for i in range(5)) + "@example.com" for i in range(n)]
    keys = ["".join(random.choice(letters_digits) for i in range(32)) for i in range(n)]
    ip_addresses = REPLACEMENTS_IP
    return {"EMAIL": emails, "KEY": keys, "IP_ADDRESS": ip_addresses}

def replace_ip(value, replacements_dict):
    try:
        ipaddress.IPv4Address(value)
        return random.choice(replacements_dict["IP_ADDRESS"]["IPv4"])
    except ValueError:
        try:
            ipaddress.IPv6Address(value)
            return random.choice(replacements_dict["IP_ADDRESS"]["IPv6"])
        except ValueError:
            print("Invalid IP address")
            return value

def is_private_ip(ip):
    ip = ipaddress.ip_address(ip)
    return ip.is_private


def redact_pii_text(text, secrets, replacements, add_references=True):
    secrets = load_json(secrets)
    if not secrets or not isinstance(secrets, list):
        return text, "", False

    modified = False
    references = []

    for secret in sorted(secrets, key=lambda x: x["start"], reverse=True):
        if secret["tag"] == "IP_ADDRESS" and (is_private_ip(secret["value"]) or secret["value"] in POPULAR_DNS_SERVERS):
            continue

        modified = True
        replacement_list = replacements.get(secret["tag"], [secret["value"]])
        replacement = replacement_list[0] if isinstance(replacement_list, list) else replacement_list

        # If replacement for IP_ADDRESS is a dictionary, extract the appropriate version
        if secret["tag"] == "IP_ADDRESS" and isinstance(replacement, dict):
            ip_version = "IPv6" if ":" in secret["value"] else "IPv4"
            replacement = replacement[ip_version][0]

        if add_references:
            references.append(f"PI:{secret['tag']}:{replacement}END_PI")

        text = text[:secret["start"]] + str(replacement) + text[secret["end"]:]

    references = "".join(references) if add_references else ""

    return text, references, modified





def redact_pii_batch(examples, replacements, add_references=True):
    new_contents = []
    references = []
    modified = []

    for example in examples:
        text, sec, has_sec = example["content"], example["secrets"], example["has_secrets"]
        if has_sec:
            if add_references:
                new_text, reference, modif = redact_pii_text(
                    text, sec[0], replacements, add_references
                )
                references.append(reference)
            else:
                new_text, modif = redact_pii_text(text, sec[0], replacements)
            new_contents.append(new_text)
            modified.append(modif)
        else:
            new_contents.append(text)
            references.append(text)
            modified.append(False)

    result = {"new_content": new_contents, "modified": modified}
    if add_references:
        result.update({"references": references})
    return result


