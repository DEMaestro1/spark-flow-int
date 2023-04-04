import datetime
import configparser
from pathlib import Path
from airflow.models import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator


#parsing configuration file in same directory for postgres details, other DBs can be used if needed
parser = configparser.ConfigParser()
p = Path(__file__).with_name('configuration.conf')
parser.read(p.absolute())
postgresUser = parser.get('postgres_config', 'postgres_username')
postgresPass = parser.get('postgres_config', 'postgres_password')
postgresHost = parser.get('postgres_config', 'postgres_hostname')
postgresPort = parser.get('postgres_config', 'postgres_port')
postgresDBName = parser.get('postgres_config', 'postgres_db')
sqlDb = 'postgresql'

#defining the URL for postgres, in this case it will be equivalent to jdbc:postgres://postgres-db:5432/poverty
postgresURL = f'jdbc:{sqlDb}://{postgresHost}:{postgresPort}/{postgresDBName}'

#File path
filePath = '/usr/local/files'
taskPath = '/opt/bitnami/spark/tasks'

#Jar required to store data in postgres DB
postgresqlJar = '/opt/bitnami/spark/jars/postgresql-42.6.0.jar'

# DAG arguments
defaultArgs = {
    'owner': 'New_O',
    'depends_on_past': False,
    'start_date': datetime.datetime(2023, 1, 1),
    'retries': 0,
    'retry_delay': datetime.timedelta(seconds=30),
    'catchup': False
}

# DAG definition
with DAG('proc_data',
         schedule_interval ='@daily',
         default_args = defaultArgs,
         catchup = False) as dag:
         
    transformation_job = SparkSubmitOperator(
        task_id = 'transformation_job',
        application = f'{taskPath}/transformationProcess.py', 
        name = 'process_data',
        conn_id = 'spark_default',
        application_args = [filePath]
        )     
     
    #Passing the postgres jar as well as the configurations for postgres   
    load_job = SparkSubmitOperator(
        task_id = 'load_job',
        application = f'{taskPath}/loadProcess.py', 
        name = 'load_data',
        conn_id = 'spark_default',
        jars = postgresqlJar,
        driver_class_path = postgresqlJar,
        application_args = [filePath, postgresURL, postgresUser, postgresPass]
        )     


    # set tasks relations (the order the tasks are executed)
    transformation_job >> load_job