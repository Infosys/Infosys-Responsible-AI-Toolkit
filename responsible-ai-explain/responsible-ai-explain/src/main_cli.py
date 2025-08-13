''' 
Copyright 2024-2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), 
to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies 
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE 
AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import argparse

from explain.service.service import ExplainService as service
from explain.config.logger import CustomLogger

log=CustomLogger()

try:
    parser = argparse.ArgumentParser()
    parser.add_argument("--explain_global")
    parser.add_argument("--explain_local")
    parser.add_argument("--explain_localTabular")
    parser.add_argument("--explain_localImage")
    parser.add_argument("--config")

    args = parser.parse_args()
    log.info(f'args: {args}')
    config = vars(args)
    log.info(f'config: {config}')

    explain_global = config['explain_global']
    log.info(f'explain_global: {explain_global}')
    explain_local = config['explain_local']
    log.info(f'explain_local: {explain_local}')
    explain_localTabular = config['explain_localTabular']
    log.info(f'explain_localTabular: {explain_localTabular}')
    explain_localImage = config['explain_localImage']
    log.info(f'explain_localImage: {explain_localImage}')
    config_details = {}
    if config['config'] is not None:
        config_details = eval(config['config'])
    log.info(f'config_details: {config_details}')

except Exception as e:
    log.error(f"Exception: {e}")


class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class Explainability:

    @staticmethod
    def run():
        if explain_local == 'True':
            config_data = config_details['explain']['explain_local']
            data = AttributeDict(config_data)
            response = service.local_explain(data)
            log.info(response)

        if explain_global == 'True':
            config_data = config_details['explain']['explain_global']
            data = AttributeDict(config_data)
            response = service.global_explain(data)
            log.info(response)

        if explain_localTabular == 'True':
            config_data = config_details['explain']['explain_localTabular']
            data = AttributeDict(config_data)
            response = service.localTabular_explain(data)
            log.info(response)
        if explain_localImage == 'True':
            config_data = config_details['explain']['explain_localImage']
            data = AttributeDict(config_data)
            response = service.localImage_explain(data)
            log.info(response)


try:
    obj = Explainability
    obj.run()

except Exception as e:
    log.error(f"Exception: {e}")
