from airflow import DAG
from datetime import datetime, timedelta

#from airflow.operators import SalesforceToFileOperator
from airflow.operators.salesforce_to_file_plugin import SalesforceToFileOperator

#from airflow.contrib.operators import file_to_gcs
#from airflow.contrib.operators import gcs_to_bq

import os


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2015, 6, 1),
    'email': ['atereshenkov@modeln.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}

dag = DAG('extract_sfdc', default_args=default_args)

base_path = '/usr/local/airflow/data'
output_filename = "account.json"
output_filepath = os.path.join(base_path, output_filename)

output_schemaname = "account_schema.json"
output_schema = os.path.join(base_path, output_schemaname)

# these values can and should change based on your unique setup
# the GCS BUCKET is the bucket on Google Cloud Storage where you want the files to live
# GCS_CONN_ID is the name of the Airflow connection that holds your credentials to connect to the Google API
# SF_CONN_ID is the name of the Airflow connection that holds your crednetials to connect to your Salesforce API
#
# To setup connections:
#   - launch the airflow webserver:
#       >$ airflow webserver
#   - Go to Admin->Connections and then click on "Create"
#   - select the corresponding connection type and enter in your info
#       - For Google Cloud Services use "Google Cloud Platform"
#       - For Salesforce use "HTTP"
#           * username:     your salesforce username
#           * passsword:    your salesforce password
#           * extra:        you should put a JSON structure here that contains your security token if your SF implemntation requires it
#               - {"security_token": "YOUR_SECURITY_TOKEN_HERE"}

#GCS_BUCKET = "YOUR_BUCKET_HERE"
#GCS_CONN_ID = "google_cloud_storage_default"
SF_CONN_ID = "PD_SFDC"

# query salesforce
# the SalesforceToFileOperator takes in a conection name
# to define the connection, go to Admin -> Connections
# it uses the HTTP connection type
# the security token is included in the "Extras" field, which allows you to define extra attributes in a JSON format
#   {"security_token":"asdasdasd"}
t1 = SalesforceToFileOperator(
    task_id =               "get_model_salesforce",
    obj =                   "Account",          # the object we are querying
    fields =                ["Name", "Id"],    # you can use this to limit the fields that are queried
    conn_id =               SF_CONN_ID,         # name of the Airflow connection that has our SF credentials
    output =                output_filepath,    # file where the resulting data is stored
    output_schemafile =     output_schema,      # tell the operator that we want a file of the resulting schema
    output_schematype =     "BQ",               # specify that we want to generate a schema file for BigQuery
    fmt =                   "ndjson",           # write the file as newline deliminated json.  Other options include CSV and JSON
    record_time_added =     True,               # add a column to the output that records the time at which the data was fetched
    coerce_to_timestamp =   True,               # coerce all date and datetime fields into Unix timestamps (UTC)
    dag =                   dag
)
