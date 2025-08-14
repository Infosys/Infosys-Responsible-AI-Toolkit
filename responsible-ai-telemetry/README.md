# Responsible AI Telemetry

## Introduction
The telemetry repository is used for getting the telemetry data from various other API's to push to elastic and visualize in the kibana.

## Requirements
- Python 3.9 - 3.11
- VSCode

## Environment Variables
Locate the `.env` file, which contains keys like the following:

```sh
## TO RUN IN LOCAL SYSTEM UNCOMEENT BELOW LINES
# CHUNK_SIZE=1
# DELAY=120
# ERROR_ENVIRONMENT="local"
# ELASTIC_URL="http://<elastic_ip>:<port>/"
# ELASTIC_TIMEOUT=10
```

Replace the elastic URL with your elasticsearch IP address and uncomment all the above lines.

## Steps to run this module
1. Clone this repository in vscode

2. Create a virtual environment for python using cmd:
   ```sh
   python -m venv <env-name>
   ```

3. Activate the virtual environment:
   - On Windows:
     ```sh
     .\myenv\Scripts\activate
     ```
   - On Linux/Mac:
     ```sh
     source myenv/bin/activate
     ```

4. Install all the dependencies from requirements.txt:
   ```sh
   pip install -r path/to/requirements.txt
   ```

5. Open `.env` file in vscode and configure the entries in it

6. In the virtual environment go to src folder of cloned repository and run:
   ```sh
   python main.py
   ```

7. Access the API documentation at:
   ```
   http://localhost:<portno.>/rai/v1/telemetry/docs
   ```
   Use the Port No that is configured in `.env` file.

## Steps for running Elasticsearch and Kibana locally

1. Download Elasticsearch, e.g., [Elasticsearch 8.11.1](https://www.elastic.co/downloads/past-releases/elasticsearch-8-11-1)

2. Download Kibana compatible with your Elasticsearch version, e.g., [Kibana 8.11.3](https://www.elastic.co/downloads/past-releases/kibana-8-11-3)

3. Ensure you have Java JDK installed, if not download a [compatible version](https://www.oracle.com/java/technologies/downloads/)

4. Extract the Elasticsearch and Kibana zip files to separate folders

5. Configure Elasticsearch:
   - Navigate to `elasticsearch folder --> Config --> elasticsearch.yml`
   - Edit the file and uncomment these values:
     ```yaml
     cluster.name:
     node.name: node-1
     network.host: 127.0.0.1
     discovery.seed_hosts: "127.0.0.1"
     cluster.initial_master_nodes: "node-1"
     http.port: 9200
     ```
   - Add these values at the end of file:
     ```yaml
     xpack.security.enabled: false
     xpack.security.transport.ssl.enabled: false
     xpack.security.http.ssl.enabled: false
     http.cors.enabled: true
     http.cors.allow-origin: '*'
     ```

6. Start Elasticsearch:
   - Go to the `bin` folder in the Elasticsearch directory
   - Open cmd and run `elasticsearch.bat`
   - When loaded, verify by opening `http://localhost:9200` in browser

7. Start Kibana:
   - Go to the Kibana `bin` folder
   - Open cmd and run `kibana.bat`
   - Kibana will be available at `http://localhost:5601` after a few minutes

8. Update your `.env` file to use `http://localhost:9200` as the Elasticsearch URL

## Creating Dashboards in Kibana

### Accessing the Data
1. Data from services like Privacy are exported to Elasticsearch with specific indices
   - For example, privacy service data is stored in index: `privacyindexv2`

### Creating Data Views in Kibana
1. Login to Kibana at `http://localhost:5601/`
2. Navigate to Stack Management → Data Views
3. Click "Create data view"
4. For privacy data, use:
   - Index pattern: `privacyindexv2`
   - Time field: `date`
5. Click "Save data view"

### Creating Visualizations
1. Navigate to Visualizations → Create visualization
2. Select a visualization type (bar chart, line chart, pie chart, etc.)
3. Choose your data view (e.g., `privacyindexv2`)
4. Configure metrics and buckets:
   - For privacy data, useful metrics include:
     - Count of records by `response.type`
     - Distribution by `tenant`
     - Timeline of requests by `date`
5. Save your visualization with a descriptive name

### Building Dashboards
1. Navigate to Dashboard → Create dashboard
2. Click "Add" to include your saved visualizations
3. Arrange visualizations on the dashboard grid
4. Add filters at the dashboard level (e.g., filter by tenant)
5. Save your dashboard with a descriptive name

### Example: Privacy Data Dashboard
The privacy service exports data with the following structure:
- Index: `privacyindexv2`
- Key fields: `tenant`, `apiname`, `user`, `date`, `request`, `response`

To create an effective privacy monitoring dashboard:

1. Create these visualizations:
   - **Privacy Detection Types**: Pie chart showing counts by `response.type`
   - **Privacy Requests Timeline**: Line chart showing requests over time
   - **Detection Details**: Data table with columns for `date`, `apiname`, `user`, `response.type`, and `response.score`
   - **Detection Count by API**: Bar chart showing count by `apiname`

2. Combine these visualizations into a dashboard called "Privacy Monitoring Dashboard"

3. Access the dashboard at:
   ```
   http://localhost:5601/app/dashboards
   ```
   Then search for "Privacy Monitoring Dashboard"

4. Apply filters to focus on specific tenants, date ranges, or high-confidence detections

## License
The source code for the project is licensed under the MIT license, which you can find in the [LICENSE.txt](License.md) file.

## Contact
If you have more questions or need further insights please feel free to connect with us @ Infosysraitoolkit@infosys.com

