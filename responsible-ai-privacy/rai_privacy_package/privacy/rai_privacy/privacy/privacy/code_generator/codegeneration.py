'''
MIT license https://opensource.org/licenses/MIT Copyright 2024 Infosys Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import os
import subprocess
import shutil
# from dotenv import load_dotenv
# load_dotenv()

# def test():
#     print(os.environ)
#     #test = os.environ["FILE_NAME"]
#     #print(test)
    
#     print(os.getenv('FILE_NAME'))


# FILE CREATION
def create_new_recognizer_file(file_name, regex_expression):
    template_file = "template_recognizer.py"  # Assign the template file name directly
    # Get the absolute path of the current script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # print(script_dir)
    # Construct the full path to the template file
    template_file_path = os.path.join(script_dir, template_file)
    #output file path
    # output_directory = os.path.join(script_dir, "..\\..\\..\\..\\presidio_analyzer\\presidio_analyzer\\Infosys_presidio_analyzer\\presidio_analyzer\\presidio_analyzer\\predefined_recognizers")
    output_directory = "../../presidio_analyzer/presidio_analyzer/Infosys_presidio_analyzer/presidio_analyzer/presidio_analyzer/predefined_recognizers/"
    os.makedirs(output_directory, exist_ok=True)
    #new file name
    new_file = f"{file_name}_recognizer.py"
    #combine the path
    output_path = os.path.join(output_directory, new_file)
    with open(template_file_path, "r") as f:
        template_content = f.read()

    # Replace the placeholder values in the template
    # have to start replacing the content in the template file
    # Replace the class name in the template
    new_content = template_content.replace("Class_Name", file_name)
    # Replace the supported_entity parameter value
    supported_entity = file_name.upper()
    new_content = new_content.replace('supported_entity: str = "AADHAR_NUMBER"',
                                      f'supported_entity: str = "{supported_entity}"')
    # Replacing the pattern name
    new_content = new_content.replace("pattern_name", f"{file_name.lower()}_pattern")
    
    # Replacing the regex expression
    new_content = new_content.replace("REGEX_PATTERN", regex_expression)
   # Write the modified content to the new file at the specified output path
    with open(output_path, "w") as f:
        f.write(new_content)
    print(f"Created new recognizer file: {new_file}")
    
# ADDING IMPORTS IN RECOGNIZERS REGISTRY

def modify_recognizer_registry(file_name):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    recognizer_registry_file = os.path.join(
        script_dir,
        "../../../../presidio_analyzer/presidio_analyzer/Infosys_presidio_analyzer/presidio_analyzer/presidio_analyzer/recognizer_registry/recognizer_registry.py",
    )

    # Check if the class name is already imported
    with open(recognizer_registry_file, "r") as f:
        lines = f.readlines()
    
    class_name = f"class {file_name}"
    existing_lines = [line.strip().lower() for line in lines]
    new_import_line = f"    {file_name},"

    # Check if the class name is already imported
    is_imported = any(class_name.lower() == line.lower().strip() for line in existing_lines)

    # If the class name is already imported, skip the addition
    if is_imported:
        print(f"Skipping addition: Import for {file_name} already exists")
        return

    # Find the position to insert the new import line
    import_section_start = existing_lines.index("from presidio_analyzer.predefined_recognizers import (") + 1
    import_section_end = existing_lines.index(")", import_section_start)
    
    en_section_start = lines.index("            \"en\": [\n")  # Find the start of the 'en' section
    en_section_end = lines.index("            ],\n", en_section_start)  # Find the end of the 'en' section
    
    # Check if the import statement already exists in the 'en' section
    is_imported_en = any(file_name.lower() in line.lower().strip() for line in existing_lines[en_section_start:en_section_end])

    # If the import statement already exists in the 'en' section, skip the addition
    if is_imported_en:
        print(f"Skipping addition: Import for {file_name} already exists in the 'en' section")
        return

    # Add the filename import to the 'en' section
    lines.insert(en_section_end, f"                {file_name},\n")
    # Insert the new import line before the closing parenthesis
    lines.insert(import_section_end, new_import_line + "\n")

    # Write the modified content back to the file
    with open(recognizer_registry_file, "w") as f:
        f.writelines(lines)

    print(f"Modified recognizer_registry.py: Added import for {file_name}")


# def modify_recognizer_registry(file_name):
#     script_dir = os.path.dirname(os.path.abspath(__file__))
#     recognizer_registry_file = os.path.join(script_dir, "../Packages/presidio_analyzer/presidio_analyzer/presidio_analyzer/presidio_analyzer/presidio_analyzer/recognizer_registry/recognizer_registry.py")

#     # Check if the class name is already imported
#     with open(recognizer_registry_file, "r") as f:
#         lines = f.readlines()
    
    
#     class_name = f"class {file_name}"
#     existing_lines = [line.strip().lower() for line in lines]
#     new_import_line = f"    {file_name},"
    
    
#     # Check if the class name is already imported
#     is_imported = any(class_name.lower() == line.lower().strip() for line in existing_lines)

#     # If the class name is already imported, skip the addition
#     if is_imported:
#         print(f"Skipping addition: Import for {file_name} already exists")
#         return

#     # Find the position to insert the new import line
#     import_section_start = existing_lines.index("from presidio_analyzer.predefined_recognizers import (") + 1
#     import_section_end = existing_lines.index(")", import_section_start)
#     en_section_start = lines.index("            \"en\": [\n")  # Find the start of the 'en' section
#     en_section_end = lines.index("            ],\n", en_section_start)  # Find the end of the 'en' section
#     # Add the filename import to the 'en' section
#     lines.insert(en_section_end, f"                {file_name},\n")
#     # Insert the new import line before the closing parenthesis
#     lines.insert(import_section_end, new_import_line + "\n")

#     # Write the modified content back to the file
#     with open(recognizer_registry_file, "w") as f:
#         f.writelines(lines)

#     print(f"Modified recognizer_registry.py: Added import for {file_name}")
    
# Adding import in initpy of predefined recognizers

def modify_init_py(file_name):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    init_py_file = os.path.join(script_dir, "../../../../presidio_analyzer/presidio_analyzer/Infosys_presidio_analyzer/presidio_analyzer/presidio_analyzer/predefined_recognizers/__init__.py")

    # Check if the import statement is already present
    with open(init_py_file, "r") as f:
        lines = f.readlines()

    import_line = f"from .{file_name}_recognizer import {file_name}\n"

    # Check if the import statement is already present, skip the addition
    is_imported = any(import_line.strip() == line.strip() for line in lines)

    if is_imported:
        print(f"Skipping addition: Import for {file_name} already exists in __init__.py")
        return

   # Find the position to insert the new import line
    import_section_end = next(i for i, line in enumerate(lines) if not line.startswith("from "))

    # Insert the new import line after the last import statement
    lines.insert(import_section_end + 1, import_line)
    # Write the modified content back to the file
    with open(init_py_file, "w") as f:
        f.writelines(lines)

    print(f"Modified __init__.py: Added import for {file_name}")

    
# MAKING OF WHEEL FILES


import os

def run_wheel_creation_commands():
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    directory = os.path.join(script_dir, "../../../../presidio_analyzer/presidio_analyzer/Infosys_presidio_analyzer")
    # Specify the directory where you want to run the commands
    
    # Change to the specified directory
    os.chdir(directory)

    # Command 1: pip install pyc_wheel build
    command1 = "pip install pyc_wheel build"
    subprocess.run(command1, shell=True, check=True)

    # Command 2: python create_wheel_file.py
    command2 = "python create_wheel_file.py"
    subprocess.run(command2, shell=True, check=True)


def copy_wheel_file():
    script_dirsourcewheel = os.path.dirname(os.path.abspath(__file__))
    script_dirdestinationwheel = os.path.dirname(os.path.abspath(__file__))
    
    source_directory = os.path.join(script_dirsourcewheel, "../../../../presidio_analyzer/presidio_analyzer/Infosys_presidio_analyzer")
    # Get the path of the wheel file
    source_wheel_file = os.path.join(source_directory, "dist", "presidio_analyzer-4.0.5-py3-none-any.whl")
    
    destination_directory = os.path.join(script_dirdestinationwheel, "../../../lib")
    
     # Get the path of the destination wheel file
    destination_wheel_file = os.path.join(destination_directory, "presidio_analyzer-4.0.5-py3-none-any.whl")
    
    # Remove the destination wheel file if it already exists
    if os.path.exists(destination_wheel_file):
        os.remove(destination_wheel_file)

     # Copy the wheel file to the destination directory
    shutil.copy2(source_wheel_file, destination_wheel_file)

    # Change to the destination directory
    os.chdir(destination_directory)

    # Uninstall the previous version of presidio_analyzer
    uninstall_command = "pip uninstall -y presidio_analyzer-4.0.5-py3-none-any.whl"
    subprocess.run(uninstall_command, shell=True, check=True)

    # Install the new version of presidio_analyzer
    install_command = "pip install presidio_analyzer-4.0.5-py3-none-any.whl"
    subprocess.run(install_command, shell=True, check=True)

    print("Wheel file copied and installed successfully.")


# # Call the function with the specified directory
# run_wheel_creation_commands(directory)


    
    




    
    






