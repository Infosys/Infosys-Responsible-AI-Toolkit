/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
const { exec } = require('shelljs');
const fs = require('fs');
const path = require('path');

const proxyConfigPath = 'proxy.config.json';
const angularPath = 'angular.json';
const appConstantPath = 'src/app/app.constants.ts';
//const stylePath = 'styles.scss';
const envFilePath = 'src/environments/environment.ts';
const urlListFilePath = 'src/app/utils/urlList.ts';
const webpackConfigPath = 'webpack.config.js';
const appmodulePath = 'src/app/app.module.ts';

const URLDATA = {
    SERVER_API_URL: null,
    FRONTEND_URL: null,
    NG_SERVE_CMD: null,
    LOGIN_USER_NAME: null,
    LOGIN_USER_CRED: null,
    ADMIN_URL: null,
    MFE_URL: null,
    MFE_AUTHENTICATE: null,
    MFE_ACCOUNT: null,
    MFE_MANIFEST: null,
    AZURE_CLIENTID: null,
    AZURE_AUTHORITY: null,
    AZURE_REDIRECTURI: null,
    SSO_BASED_LOGIN: null,
    TELEMETRY_DASHBOARD: null

};

const readFile = filePath => {
    return new Promise(async(resolve, reject) => {
        fs.readFile(path.normalize(filePath), 'utf8', (err, data) => {
            if (err) {
                console.log(err);
                reject(err);
            }
            resolve(data);
        });
    });
};

const writeFile = (filePath, data) => {
    return new Promise(async(resolve, reject) => {
        fs.writeFile(path.normalize(filePath), data, 'utf8', err => {
            if (err) {
                console.log(err);
                reject(err);
            }
            console.log('Successfully written :: ' + filePath);
            resolve('success');
        });
    });
};

// const NgServeProxyConfig = function(err) {
//     if (err) return console.log(err);
//     console.log('EXECUTING ::  ng serve --host 0.0.0.0 --port 30010  --disable-host-check');
//     exec.execSync(URLDATA.NG_SERVE_CMD, { stdio: 'inherit' });
// };
const NgServeProxyConfig = () => {
    if (!URLDATA.NG_SERVE_CMD) {
        console.error('NG_SERVE_CMD is not set in URLDATA');
        return;
    }

    // Sanitize and validate the command
    const sanitizedCommand = sanitizeCommandInput(URLDATA.NG_SERVE_CMD);
    if (!validateCommand(sanitizedCommand)) {
        console.error('Invalid command detected');
        return;
    }

    console.log('Executing ng serve with command:', sanitizedCommand);
    exec(sanitizedCommand, { stdio: 'inherit' }, (error, stdout, stderr) => {
        if (error) {
            console.error(`Error executing ng serve: ${error.message}`);
            return;
        }
        if (stderr) {
            console.error(`stderr: ${stderr}`);
            return;
        }
        console.log(`stdout: ${stdout}`);
    });
};
const sanitizeCommandInput = (input) => {
    console.log("sanitize")
        // This allows alphanumeric characters, spaces, hyphens, and equals signs
    const sanitized = input.replace(/[^a-zA-Z0-9\s\-=\.:/]/g, '');
    return sanitized;
};
const validateCommand = (command) => {
    console.log("validate")
        // Check if the command starts with 'ng' and contains only safe arguments
    return /^ng\s/.test(command); // 'ng' followed by any valid arguments
};

const updateProxyConfig = async() => {
    return new Promise(async(resolve, reject) => {
        console.log('updating proxy config data');
        const proxyConfigFileData = await readFile(proxyConfigPath);
        const proxyConfigFileData2 = proxyConfigFileData
            .replace(/MFE_AUTHENTICATE/g, URLDATA.MFE_AUTHENTICATE)
            .replace(/MFE_ACCOUNT/g, URLDATA.MFE_ACCOUNT)
            .replace(/MFE_MANIFEST/g, URLDATA.MFE_MANIFEST)

        const writeRes = await writeFile(proxyConfigPath, proxyConfigFileData2);
        resolve(writeRes);
    });
};

const updateAngular = async() => {
    return new Promise(async(resolve, reject) => {
        console.log('updating Angular data');
        const angularFileData = await readFile(angularPath);
        const angularFileData2 = angularFileData.replace(/FRONTEND_URL/g, URLDATA.FRONTEND_URL);

        const writeRes = await writeFile(angularPath, angularFileData2);
        resolve(writeRes);
    });
};
const updateStyle = async() => {
    return new Promise(async(resolve, reject) => {
        console.log('updating Style data');
        const styleFileData = await readFile(stylePath);
        const styleFileData2 = styleFileData.replace(/HOST_URL/g, URLDATA.HOST_URL);

        const writeRes = await writeFile(stylePath, styleFileData2);
        resolve(writeRes);
    });
};

const updateAppConstant = async() => {
    return new Promise(async(resolve, reject) => {
        console.log('updating app constant data');
        const appConstantFileData = await readFile(appConstantPath);
        const appConstantFileData2 = appConstantFileData
            .replace(/LOGIN_USER_NAME/g, URLDATA.LOGIN_USER_NAME)
            .replace(/LOGIN_USER_CRED/g, URLDATA.LOGIN_USER_CRED)
        const writeRes = await writeFile(appConstantPath, appConstantFileData2);
        resolve(writeRes);
    });
};
const updateAppModuleConstant = async() => {
    return new Promise(async(resolve, reject) => {
        console.log('updating app constant data');
        const appModuleConstantFileData = await readFile(appmodulePath);
        const appModuleConstantFileData2 = appModuleConstantFileData
            .replace(/urlList.azure_clientid/g, URLDATA.AZURE_CLIENTID)
            .replace(/urlList.azure_redirecturi/g, URLDATA.AZURE_REDIRECTURI)
            .replace(/urlList.azure_authority/g, URLDATA.AZURE_AUTHORITY)
        const writeRes = await writeFile(appmodulePath, appModuleConstantFileData2);
        resolve(writeRes);
    });
};

const updateEnvFile = async() => {
    return new Promise(async(resolve, reject) => {
        console.log('updating env data');
        const envFileData = await readFile(envFilePath);
        const fileData = envFileData
            .replace(/ADMIN_URL/g, URLDATA.ADMIN_URL)
            .replace(/'SSO_BASED_LOGIN'/g, URLDATA.SSO_BASED_LOGIN)

        const writeRes = await writeFile(envFilePath, fileData);
        resolve(writeRes);
    });
};

const updateWebpackConfig = async() => {
    return new Promise(async(resolve, reject) => {
        console.log('updating webpack config data');
        const webpackConfigFileData = await readFile(webpackConfigPath);
        const webpackConfigFileData2 = webpackConfigFileData.replace(/MFE_URL/g, URLDATA.MFE_URL);

        const writeRes = await writeFile(webpackConfigPath, webpackConfigFileData2);
        resolve(writeRes);
    });
};

const updateURLlistTs = async() => {
    return new Promise(async(resolve, reject) => {
        console.log('updating urlList.ts data');
        const proxyConfigFileData = await readFile(urlListFilePath);
        let updatedData = proxyConfigFileData
            .replace(/SERVER_API_URL/g, URLDATA.SERVER_API_URL)
            .replace(/FRONTEND_URL/g, URLDATA.FRONTEND_URL)
            .replace(/ADMIN_URL/g, URLDATA.ADMIN_URL)
            .replace(/LOGIN_USER_NAME/g, URLDATA.LOGIN_USER_NAME)
            .replace(/LOGIN_USER_CRED/g, URLDATA.LOGIN_USER_CRED)
            .replace(/MFE_URL/g, URLDATA.MFE_URL)
            .replace(/MFE_AUTHENTICATE/g, URLDATA.MFE_AUTHENTICATE)
            .replace(/MFE_ACCOUNT/g, URLDATA.MFE_ACCOUNT)
            .replace(/MFE_MANIFEST/g, URLDATA.MFE_MANIFEST)
            .replace(/AZURE_CLIENTID/g, URLDATA.AZURE_CLIENTID)
            .replace(/AZURE_AUTHORITY/g, URLDATA.AZURE_AUTHORITY)
            .replace(/AZURE_REDIRECTURI/g, URLDATA.AZURE_REDIRECTURI)
            .replace(/SSO_BASED_LOGIN/g, URLDATA.SSO_BASED_LOGIN)
            .replace(/TELEMETRY_DASHBOARD/g, URLDATA.TELEMETRY_DASHBOARD)

        const writeRes = await writeFile(urlListFilePath, updatedData);
        resolve(writeRes);
    });
};

const setDataFromENV = () => {
    (URLDATA['SERVER_API_URL'] = process.env['SERVER_API_URL']),
    (URLDATA['FRONTEND_URL'] = process.env['FRONTEND_URL']),
    (URLDATA['ADMIN_URL'] = process.env['ADMIN_URL']),
    (URLDATA['LOGIN_USER_NAME'] = process.env['LOGIN_USER_NAME']),
    (URLDATA['LOGIN_USER_CRED'] = process.env['LOGIN_USER_CRED']),
    (URLDATA['NG_SERVE_CMD'] = process.env['NG_SERVE_CMD']),
    (URLDATA['MFE_URL'] = process.env['MFE_URL']),
    (URLDATA['MFE_AUTHENTICATE'] = process.env['MFE_URL'] + "/api/authenticate/"),
    (URLDATA['MFE_ACCOUNT'] = process.env['MFE_URL'] + "/api/account/"),
    (URLDATA['MFE_MANIFEST'] = process.env['MFE_URL'] + "/manifest.webapp");
    (URLDATA['AZURE_CLIENTID'] = process.env['AZURE_CLIENTID']),
    (URLDATA['AZURE_AUTHORITY'] = process.env['AZURE_AUTHORITY']),
    (URLDATA['AZURE_REDIRECTURI'] = process.env['AZURE_REDIRECTURI']);
    (URLDATA['SSO_BASED_LOGIN'] = process.env['SSO_BASED_LOGIN']);
    (URLDATA['TELEMETRY_DASHBOARD'] = process.env['TELEMETRY_DASHBOARD']);
};

const runLocally = async() => {
    (URLDATA['SERVER_API_URL'] = 'http://localhost:30019/v1/rai/backend'),
    (URLDATA['FRONTEND_URL'] = 'http://0.0.0.0:30010'),
    (URLDATA['LOGIN_USER_NAME'] = 'admin'),
    (URLDATA['LOGIN_USER_CRED'] = 'admin'),
    (URLDATA['NG_SERVE_CMD'] = 'ng serve --host 0.0.0.0 --port 30010 '),
    (URLDATA['ADMIN_URL'] = "http://localhost:30016"),
    (URLDATA['MFE_URL'] = 'http://localhost:30055'),
    (URLDATA['MFE_AUTHENTICATE'] = 'http://localhost:30055/api/authenticate/'),
    (URLDATA['MFE_ACCOUNT'] = 'http://localhost:30055/api/account/'),
    (URLDATA['MFE_MANIFEST'] = 'http://localhost:30055/manifest.webapp');
    (URLDATA['AZURE_AUTHORITY'] = '<AUTHORITY>'),
    (URLDATA['AZURE_REDIRECTURI'] = '<REDIRECT_URI>'),
    (URLDATA['AZURE_CLIENTID'] = '<CLIENT_ID>');
    (URLDATA['SSO_BASED_LOGIN'] = false);
    (URLDATA['TELEMETRY_DASHBOARD'] = '<TELEMETRY_DASHBOARD>');
};

const runApplication = async function() {
    setDataFromENV();
    // await runLocally();

    const proxyConfigRes = await updateProxyConfig();
    const webpackConfigRes = await updateWebpackConfig();
    const URLlistTsRes = await updateURLlistTs();
    const EnvFile = await updateEnvFile();
    const AngularFile = await updateAngular();
    // const StyleFile = await updateStyle();
    const AppConstantFile = await updateAppConstant();
    // const AppModuleConstantFile = await updateAppModuleConstant();
    NgServeProxyConfig();
};

runApplication();