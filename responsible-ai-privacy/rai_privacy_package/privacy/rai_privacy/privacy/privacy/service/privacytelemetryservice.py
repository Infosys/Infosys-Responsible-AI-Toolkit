'''
MIT license https://opensource.org/licenses/MIT Copyright 2024 Infosys Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
class PrivacyTelemetryRequest:
    def __init__(self, tenant, apiname, date,user,beginOffset,endOffset,score,responseText,restype, portfolio=None, accountname=None, exclusion_list=None, entityrecognised=None,inputText=None):
        self.tenant = tenant
        self.apiname = apiname
        self.date = date
        self.user = user
        self.privacy_requests = {
            'portfolio_name': str(portfolio) if portfolio is not None else "None",
            'account_name': str(accountname) if accountname is not None else "None",
            'exclusion_list': exclusion_list.split(',') if exclusion_list is not None else [],
            'inputText': str(inputText) if inputText is not None else "None",
        }
        self.privacy_response = {
            'type': str(restype) if restype is not None else "None",
            'beginOffset': float(beginOffset) if beginOffset is not None else 0,
            'endOffset': float(endOffset) if endOffset is not None else 0,
            'score': float(score) if score is not None else "None",
            'responseText': str(responseText) if responseText is not None else "None",

        }