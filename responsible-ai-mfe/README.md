# RAI  MicroFrontend(MFE)

## Prerequisite

Before you can build this project, you must install and configure the following dependencies on your machine:

1.	Install Node.js
    Ensure that Node.js version is higher than v18 (preferably the latest stable version. v22.5.1 when developed)
2.	Install Angular CLI
    Install Angular CLI v15.2.9 to align with the application's version:
            ```
                npm install -g @angular/cli@15.2.9
            ```
3.	Update Environment Variables
    Add the npm path to your system’s environment variables with the variable name Path.
    Example 
    `C:\Users\<username>\AppData\Roaming\npm`.
4. Now CLI will be available .

## To Run Locally

After installing Node & following above steps, you should be able to run the following command to install development tools.
1. 	Verify Dependencies
        After cloning, inspect the package.json file. It contains the list of dependencies required for the application along with their specific versions.

2.	Install Dependencies
        Navigate to the root folder of the project(e.g., D:\Infosys-Responsible-AI-Toolkit\responsible-ai-mfe) and run the following command to install all necessary dependencies:
       ```
       npm install
        ```

    You will only need to run this command  also whenever dependencies change in [package.json] (package.json).

3.	Node Modules Folder :
        Once dependencies are installed, a node_modules folder will be created containing all direct and indirect dependencies. The versions of dependencies will be aligned with the lockfile (package-lock.json).

4.	Configure start.js File
    Open the start.js file and make the following modifications:
        1.	Uncomment the line:
            `await runLocally()`;

        2.	Comment the line:
            `setDataFromENV()`;

        3.	 Modify Variables in the runLocally Method
                In the runLocally method, replace the following variables with the correct values:
                    1.	MASTERURL: Endpoint for the config API from the admin module, e.g., http://localhost:4000/api/v1/rai/admin/ConfigApi.

                    2.	ENABLESEARCH: Set to true to enable internet search functionality, e.g., true.

                    3.	AUTHORITY_API: Endpoint for the page authority from the backend module, e.g., http://localhost:5000/v1/rai/backend/pageauthoritynew.

                    4. AUTH_TOKEN: Set the auth token to "Bearer None".

5.	The runLocally() method configures all values locally, while setDataFromENV()
     fetches configuration values from Nginx during server deployment.

6.	Start the Application
        In the root folder(e.g., D:\Infosys-Responsible-AI-Toolkit\responsible-ai-mfe), run the following command to start the application:
        ```
            npm start
        ```
       The application is available at `http://localhost:30055`. When you open this URL, you might only see the navbar initially, as the list of pages will be loaded when the API is called from the shell. You will be able to view the entire application once the shell and backend are up and running, as the application is embedded within the shell using the micro frontends (MFE) architecture.

We use npm scripts and [Webpack][] as our build system.
Npm is also used to manage CSS and JavaScript dependencies used in this application. You can upgrade dependencies by
specifying a newer version in [package.json](package.json). You can also run `npm update` and `npm install` to manage dependencies.
Add the `help` flag on any command to see how you can use it. For example, `npm help update`.

The `npm run` command will list all of the scripts available to run for this project.

 ### Known Issue:
 1. If Token Importance Graph doesn't show up for explainability with Canvas not found error , then uncomment this.TokenImportance() in toggleArrow() method of src/app/fm- 
 moderation/explainability-result.component.ts

 2. For template based guardrails- from UI we are passing user id as none, and hence we are able to see all the default templates that are added
 
If the user wants to use customized templates and not our default templates, they can create the customized template from ui and pass in the payload send to moderation layer the userid

### Using Angular CLI

You can also use [Angular CLI][] to generate some custom client code.

For example, the following command:

```
ng generate component my-component
```

will generate few files:

```
create src/main/webapp/app/my-component/my-component.component.html
create src/main/webapp/app/my-component/my-component.component.ts
update src/main/webapp/app/app.module.ts
```

## Dependency
 As these are frontend modules , they have dependency on these modules
1.	responsible-ai-shell
2.	responsible-ai-ModerationModel
3.	responsible-ai-explainability
4.	responsible-ai-llm-explain
5.	responsible-ai-privacy
6.  responsible-ai-moderationLayer
7.	responsible-ai-security-API
8.	responsible-ai-fairness
9.	responsible-ai-llmbenchmarking
10.	responsible-ai-backend
11.	responsible-ai-admin
12.	responsible-ai-hallucination
13.	Responsible-ai-video
14.	responsible-ai-model-detail
15.	responsible-ai-reporting-tool
16.	responsible-ai-UploadDoc
17.	responsible-ai-telemetry
18.	responsible-ai-questionnaire
19.	responsible-ai-filestorage
20. responsible-ai-safety

