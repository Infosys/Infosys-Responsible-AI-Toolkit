## RAI Prompt Moderator for Visual Studio Cpode

## Features:
The code which given as an input to visual studio copilot chat might contain the PII entities. With this extension enabled as a chat participant, it can detect the PII entities and mask them before sending to the copilot chat LLM.
If the generated code from the model is insecure. For example, the code is having weak hashing algorithm. The extension will detect it before showing it to user, it will fix the issue and will also state the issues which was identified.

## Pre-requisites
1. Angular
2. Nodejs
3. Visual Studio Code

## Running the extension via VSIX Built File

1. Make sure you have latest visual studio code installed.
2.	Open visual studio code application.
3.	Go to the extensions in right side panel.
4.	Click on the 3 dots icon and select Install From VSIX.
5.	Select the extension we have promptmoderator-0.0.1.vsix.
6.	It will get installed in the visual studio.
7.	Now open GitHub copilot chat. Type @, you will see promptModerator participant. Click on the prompt moderator.
8.	Now all the input will go through the RAI Code Moderation layer guardrails.
        Enter the below sample prompt,
        Convert this to python, 
        public class Example {
            // Class-level variable
            private static String ip = "136.226.232.200"
            public static void main(String[] args) {
                // Call a method to display the greeting
                displayGreeting(name);
        }

        System.out.println("Password:", password)
        }
8.	You can observe the output, the IP address will get masked, and you will get the output.

## Development and debugging and modification of the extension

1. Open the code in visual studio code.
2. All the logic code is in the extension.ts file. Open the file and you will see the API calls and logic. 
3. In place of PRIVACY_CODE_ANNONYMIZE_URL enter the privacy code moderation url.
4. In place of PRIVACY_CODE_SHIELD_URL enter the privacy code shield url.
5. Now to run the extension in the debug mode, click on Run --> Start Debugging. 
6. It will open a new Windows where the extension will be loaded. ALl the debug statements, console statements you will be able to see in the first window as you execute or use the extension in the newly opened window. 
7. Now make any required changes in the code and then again start the debugging.

## Creating a usable VSIX file

1. Ensure You Have VSCE Installed
VSCE (Visual Studio Code Extension Manager) is the official tool to package and publish extensions.
If you haven't installed it yet, run: npm install -g @vscode/vsce.

2. Navigate to Extension Folder
In your terminal, go to the root directory of your extension: cd path/to/your/extension.

3. Run the Packaging Command
Execute the following command to create a .vsix package: vsce package. This will generate a .vsix file in the current directory.

4. (Optional) Specify a Version
If you want to generate a .vsix with a specific version, use: vsce package --out my-extension-1.0.0.vsix.



