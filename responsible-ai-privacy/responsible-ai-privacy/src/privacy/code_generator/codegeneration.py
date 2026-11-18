'''
MIT license https://opensource.org/licenses/MIT Copyright 2024 Infosys Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import os
import subprocess
import shutil



# FILE CREATION
def create_new_recognizer_file(file_name, regex_expression):
    template_file = "template_recognizer.py" 
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_file_path = os.path.join(script_dir, template_file)
    output_directory = "../../presidio_analyzer/presidio_analyzer/Infosys_presidio_analyzer/presidio_analyzer/presidio_analyzer/predefined_recognizers/"
    os.makedirs(output_directory, exist_ok=True)
    new_file = f"{file_name}_recognizer.py"
    output_path = os.path.join(output_directory, new_file)
    with open(template_file_path, "r") as f:
        template_content = f.read()
    new_content = template_content.replace("Class_Name", file_name)
    supported_entity = file_name.upper()
    new_content = new_content.replace('supported_entity: str = "AADHAR_NUMBER"',
                                      f'supported_entity: str = "{supported_entity}"')
    new_content = new_content.replace("pattern_name", f"{file_name.lower()}_pattern")
    
    new_content = new_content.replace("REGEX_PATTERN", regex_expression)
    with open(output_path, "w") as f:
        f.write(new_content)
    print(f"Created new recognizer file: {new_file}")
    

def modify_recognizer_registry(file_name):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    recognizer_registry_file = os.path.join(
        script_dir,
        "../../../../presidio_analyzer/presidio_analyzer/Infosys_presidio_analyzer/presidio_analyzer/presidio_analyzer/recognizer_registry/recognizer_registry.py",
    )

    with open(recognizer_registry_file, "r") as f:
        lines = f.readlines()
    
    class_name = f"class {file_name}"
    existing_lines = [line.strip().lower() for line in lines]
    new_import_line = f"    {file_name},"

    is_imported = any(class_name.lower() == line.lower().strip() for line in existing_lines)

    if is_imported:
        print(f"Skipping addition: Import for {file_name} already exists")
        return

    import_section_start = existing_lines.index("from presidio_analyzer.predefined_recognizers import (") + 1
    import_section_end = existing_lines.index(")", import_section_start)
    
    en_section_start = lines.index("            \"en\": [\n")  # Find the start of the 'en' section
    en_section_end = lines.index("            ],\n", en_section_start)  # Find the end of the 'en' section
    
    is_imported_en = any(file_name.lower() in line.lower().strip() for line in existing_lines[en_section_start:en_section_end])

    if is_imported_en:
        print(f"Skipping addition: Import for {file_name} already exists in the 'en' section")
        return

    lines.insert(en_section_end, f"                {file_name},\n")
    lines.insert(import_section_end, new_import_line + "\n")

    with open(recognizer_registry_file, "w") as f:
        f.writelines(lines)

    print(f"Modified recognizer_registry.py: Added import for {file_name}")

def modify_init_py(file_name):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    init_py_file = os.path.join(script_dir, "../../../../presidio_analyzer/presidio_analyzer/Infosys_presidio_analyzer/presidio_analyzer/presidio_analyzer/predefined_recognizers/__init__.py")

    with open(init_py_file, "r") as f:
        lines = f.readlines()

    import_line = f"from .{file_name}_recognizer import {file_name}\n"

    is_imported = any(import_line.strip() == line.strip() for line in lines)

    if is_imported:
        print(f"Skipping addition: Import for {file_name} already exists in __init__.py")
        return

    import_section_end = next(i for i, line in enumerate(lines) if not line.startswith("from "))

    lines.insert(import_section_end + 1, import_line)
    with open(init_py_file, "w") as f:
        f.writelines(lines)

    print(f"Modified __init__.py: Added import for {file_name}")

    



import os

def run_wheel_creation_commands():
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    directory = os.path.join(script_dir, "../../../../presidio_analyzer/presidio_analyzer/Infosys_presidio_analyzer")
    
    os.chdir(directory)

 
    command1 = "pip install pyc_wheel build"
    subprocess.run(command1, shell=True, check=True)

    command2 = "python create_wheel_file.py"
    subprocess.run(command2, shell=True, check=True)


def copy_wheel_file():
    script_dirsourcewheel = os.path.dirname(os.path.abspath(__file__))
    script_dirdestinationwheel = os.path.dirname(os.path.abspath(__file__))
    
    source_directory = os.path.join(script_dirsourcewheel, "../../../../presidio_analyzer/presidio_analyzer/Infosys_presidio_analyzer")

    source_wheel_file = os.path.join(source_directory, "dist", "presidio_analyzer-4.0.5-py3-none-any.whl")
    
    destination_directory = os.path.join(script_dirdestinationwheel, "../../../lib")
    

    destination_wheel_file = os.path.join(destination_directory, "presidio_analyzer-4.0.5-py3-none-any.whl")
  
    if os.path.exists(destination_wheel_file):
        os.remove(destination_wheel_file)

    shutil.copy2(source_wheel_file, destination_wheel_file)


    os.chdir(destination_directory)


    uninstall_command = "pip uninstall -y presidio_analyzer-4.0.5-py3-none-any.whl"
    subprocess.run(uninstall_command, shell=True, check=True)


    install_command = "pip install presidio_analyzer-4.0.5-py3-none-any.whl"
    subprocess.run(install_command, shell=True, check=True)

    print("Wheel file copied and installed successfully.")




    
    




    
    






