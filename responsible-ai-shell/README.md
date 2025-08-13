# RAI Shell

This project was generated with [Angular CLI](https://github.com/angular/angular-cli) version 15.2.9.

## Prerequisite 

Before you can build this project, you must install and configure the following dependencies on your machine:

1.	Install Node.js
    Ensure that Node.js version is higher than v18 (preferably the latest stable version. v22.5.1 when developed).
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
        Navigate to the root folder of the project(e.g., D:\Infosys-Responsible-AI-Toolkit\responsible-ai-shell) and run the following command to install all necessary dependencies:
  	```
  	npm install
    ```

    You will only need to run this command  also whenever dependencies change in [package.json] (package.json).

4.	Node Modules Folder : 
        Once dependencies are installed, a node_modules folder will be created containing all direct and indirect dependencies. The versions of dependencies will be aligned with the lockfile (package-lock.json).

5.	Configure start.js File
    Open the start.js file and make the following modifications:
  	
        1.	Uncomment the line:
            `await runLocally()`;

        2.	Comment the line:
            `setDataFromENV()`;

        3.	 Modify Variables in the runLocally Method
                In the runLocally method, replace the following variables with the correct values:
                    1.	SERVER_API_URL: URL of the backend module running locally, e.g., http://localhost:5000/v1/rai/backend

                    2.	ADMIN_URL: URL of the admin module, e.g., http://localhost:4000.

                    3.	SSO_BASED_LOGIN: Set to False to use a form-based login page, or True to use Azure AD login, e.g., false.
                        If true, make following azure connection changes,
                            1.	AZURE_AUTHORITY: The URL for Azure Active Directory, e.g., https://login.microsoftonline.com/<Directory (tenant) ID>.

                            2.	AZURE_REDIRECTURI: The redirect URL used for Azure authentication, e.g., http://localhost:3000/callback.

                            3.	AZURE_CLIENTID: Your Azure Application (Client) ID, e.g., <Application (client) ID>.

                            4.	TELEMETRY_DASHBOARD: URL for the telemetry dashboard, e.g., http://localhost:4000/telemetry. [ OPTIONAL]


6.	The runLocally() method configures all values locally, while setDataFromENV()
     fetches configuration values from Nginx during server deployment.

7.	Start the Application
        In the root folder(e.g., D:\Infosys-Responsible-AI-Toolkit\responsible-ai-shell), run the following command to start the application:
    ```
  	npm start
    ```
       The application is available at `http://localhost:30010`. Initially it will show login form if SSO_BASED_LOGIN is set to true.To login & continue , your MFE & backend should be up & running.
       Login & authentication is handled by Backend module.
       Once you login , internally its configured to call your mfe which is running in localhost:30055.
    
    User Registration and Login Process
        To ensure a smooth user registration and login experience, follow the steps below:

        1.	Navigate to the Login Screen: Open your browser and go to http://localhost:30010 to access the login screen.
        2.	 User Registration:
            •	New users can create a profile by registering on the login page. Ensure the necessary fields (e.g., username, password, email) are filled out during registration.
        3. Login:
            •	Use the username and password created during registration to sign in.
            •	For default login use User Name: user & Password: user.
        4.	 Role Assignment:
            •	Login with User Name: admin & Password: admin, for admin level access.
            •	Upon successful registration, new users will automatically be assigned the ROLE_USER role. This role restricts access to admin pages.
        5.	 User roles can be updated either:
            •	Directly in the database by updating the role field of the user’s record.
            •	Via the User Management page: An admin can modify user roles by navigating to the User Management section in the admin interface.


We use npm scripts and [Webpack][] as our build system.
Npm is also used to manage CSS and JavaScript dependencies used in this application. You can upgrade dependencies by
specifying a newer version in [package.json](package.json). You can also run `npm update` and `npm install` to manage dependencies.
Add the `help` flag on any command to see how you can use it. For example, `npm help update`.

The `npm run` command will list all of the scripts available to run for this project.



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

## Further help

To get more help on the Angular CLI use `ng help` or go check out the [Angular CLI Overview and Command Reference](https://angular.io/cli) page.


## Dependency
 As these are frontend modules , they have dependency on these modules
1. responsible-ai-mfe
2. responsible-ai-admin
3. responsible-ai-backend
