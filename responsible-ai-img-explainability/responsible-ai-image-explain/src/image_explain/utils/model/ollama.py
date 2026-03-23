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

import ollama

class Ollama:
    def generate(model_name, prompt, image_url):
        # Generate a response using the Ollama client
        # The completion is based on a prompt provided by the user and a predefined system message

        if image_url:
            messages = [{
                'role': 'user',
                'content': prompt,
                'images': [image_url]
            }]
        else:
            messages = [{
                'role': 'user',
                'content': prompt
            }]

        if 'llama' in model_name.lower():
            model_name = 'llama3.2-vision'

        response = ollama.chat(
            model=model_name,
            messages=messages,
            options={'temperature': 0.2}
        )

        # Return the message from the generated response
        return response['message']['content']