## Introduction
The telemetry repository is used for getting the telemetry data from various other API's to push to elastic and visualize in the kibana.

## Requirements
Python 3.9 - 3.11 VSCode

## Environment Variables
1. Locate the `.env` file, which contains keys like the following:

   ```sh
   ## TO RUN IN LOCAL SYSTEM UNCOMEENT BELOW LINES
    # CHUNK_SIZE=1
    # DELAY=120
    # ERROR_ENVIRONMENT="local"
    # ELASTIC_URL="http://<elastic_ip>:<port>/"
    # ELASTIC_TIMEOUT=10
   ```
2. Replace the  elastic URL with your elasticsearch IP address. and uncomment all the above lines.

## Steps to run this module : 
1. Clone this repository in vscode
2. Create a virtual environment for python using cmd -
   `python -m venv <env-name>`
3. Activate the virtual environment:
    - On Windows:
        ```sh
        .\myenv\Scripts\activate
         ```
 
    - On Linux/Mac:
        ```sh
        source myenv/bin/activate
        ```
4. Activate the python virtual environment and install all the dependencies in requirement.txt file of the     cloned repository -
   `pip install -r path/to/requirements.txt`
5. Open .env file in vscode and configure the entries in it
6. In the virtual environment go to src folder of cloned repository and run below command to run the module-
   ```sh
    python main.py
     ```
7. PORT_NO : Use the Port No that is configured in `.env` file.

   Open the following URL in your browser:
`http://localhost:<portno.>/rai/v1/telemetry/docs`

## Steps for running elastic and kibana in local system

1. Download the elastic search, you can download any version for example, (https://www.elastic.co/downloads/past-releases/elasticsearch-8-11-1).
2. Download kibana compatible with your downloaded elastic version, for example, https://www.elastic.co/downloads/past-releases/kibana-8-11-3
3. Make sure you Java JDK installed in your system, if not download compatible version, https://www.oracle.com/java/technologies/downloads/.
4. Now extract the elastic and kibana zip files in separate folders.
5. Go to elasticsearch folder --> Config --> Elasticsearch.yml file. Open the elasticsearch yml file.
6. Edit the values if you need SSL support you might need the certficates. To run directly, comment everything in the elasticsearch yml file and uncomment values like
   - cluster.name: <Give your own name>
   - node.name: <Give name for your elastic node> --> give single node name e.g. node-1
   - network.host : 127.0.0.1 --> for locally running
   - discovery.seed_hosts: "127.0.0.1" 
   - cluster.initial_master_nodes : <give the name of above node.name value> e.g. "node-1"
   - http.port : 9200
7. Add below values at the end of file.
   xpack.security.enabled : false
   xpack.security.transport.ssl.enabled : false
   xpack.security.http.ssl.enabled : false
   http.cors.enabled : true
   http.cors.allow-origin : '*'
9. Now go bin folder in elasticsearch, open cmd inside that bin folder and run elasticsearch.bat. wait till the elasticsearch loads, after loading open localhost:9200 in browser.
10. Now go to kibana folder, then go to bin folder, open CMD and run kibana.bat.
11. The kibana will be up and running after few mins at localhost:5601.
12. Now wherever you need the elasticsearch url in all the other modules, you can give your own localhost:9200 url.
13. In localhost:5601 kibana will be running you can create graphs and other visualizations.
   

## License
The source code for the project is licensed under the MIT license, which you can find in the [LICENSE](License.md) file.

## Contact
If you have more questions or need further insights please feel free to connect with us @
Infosysraitoolkit@infosys.com
