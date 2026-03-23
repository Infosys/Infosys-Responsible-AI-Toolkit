'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''



import os
import logging
from pydantic import BaseModel
class Config(BaseModel):
    use_ssl: bool = True
    verify_ssl: bool = True
    @classmethod
    def load(cls) -> "Config":
        cfg = cls()
        return cfg

# Centralized secret retrieval (env-first; optional cloud managers via env flags)
_log = logging.getLogger(__name__)

def get_secret(name: str, default: str | None = None) -> str | None:
    """Fetch a secret from environment. Reserved for extension to cloud secret managers.

    To enable a cloud manager, set USE_KEY_VAULT/VAULT_URL or USE_AWS_SECRETS_MANAGER/AWS_REGION
    and implement the optional providers below when your environment is ready.
    """
    # Fast path: plain env
    val = os.getenv(name, default)
    return val

 


from configparser import ConfigParser, NoSectionError
import yaml
import logging
logger = logging.getLogger(__name__)


def read_config(section: str, filename: str):

    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise NoSectionError(section)

    return db

# Backward-compatible alias (deprecated): use dynamic alias to avoid linter naming rules
globals()["readConfig"] = read_config 



def read_config_yaml(filename: str):

    with open(filename) as config_file:
        config_details = yaml.safe_load(config_file)
        
    return config_details
