const ModuleFederationPlugin = require("webpack/lib/container/ModuleFederationPlugin");
const mf = require("@angular-architects/module-federation/webpack");
const path = require("path");
const share = mf.share;

const sharedMappings = new mf.SharedMappings();
sharedMappings.register(
    path.join(__dirname, 'tsconfig.json'), [ /* mapped paths to share */ ]);

module.exports = {
    output: {
        uniqueName: "shell",
        publicPath: "auto",
        scriptType: 'text/javascript'
    },
    optimization: {
        runtimeChunk: false
    },
    resolve: {
        alias: {
            ...sharedMappings.getAliases(),
        }
    },
    experiments: {
        outputModule: true,
        topLevelAwait: true
    },
    plugins: [
        new ModuleFederationPlugin({
            library: { type: "module" },
            // For remotes (please adjust)
            // name: "shell",
            // filename: "remoteEntry.js",
            // exposes: {
            //     './Component': './/src/app/app.component.ts',
            // },        

            // For hosts (please adjust)
            remotes: {
                "responsible-ui": 'http://localhost:30025' + '/remoteEntry.js',


            },

            shared: {
                "@angular/core": { singleton: true, strictVersion: true, requiredVersion: ">=12.0.0" },
                "@angular/common": { singleton: true, strictVersion: true, requiredVersion: ">=12.0.0" },
                "@angular/common/http": { singleton: true, strictVersion: true, requiredVersion: ">=12.0.0" },
                "@angular/router": { singleton: true, strictVersion: true },


                ...sharedMappings.getDescriptors()
            }

        }),
        sharedMappings.getPlugin()
    ],
    devServer: {
        historyApiFallback: true
    }
};