<h1 align="center">ETL Pipeline with Airflow, Spark, PostgreSQL and Docker</h1>

<p align="center">
  <a href="#about">About</a> •
  <a href="#scenario">Scenario</a> •
  <a href="#base-concepts">Base Concepts</a> •
  <a href="#prerequisites">Prerequisites</a> •
  <a href="#set-up">Set-up</a> •
  <a href="#installation">Installation</a> •
  <a href="#airflow-interface">Airflow Interface</a> •
  <a href="#spark-interface">Airflow Interface</a> •
  <a href="#pipeline-task-by-task">Pipeline Task by Task</a> •
  <a href="#shut-down-and-restart-airflow">Shut Down and Restart Airflow and Spark</a> 
</p>

## About

This is a small project showcasing how to build an ETL workload using Airflow, Spark and PostgreSQL with Docker being used for deployment.

A file is read from local storage(easily replaceable with an AWS S3 bucket if need be or a curl/wget command), transformed using Spark and loaded into a PostgreSQL database. 

The project is built in Python and Spark and it has 3 main parts:
  1. The Airflow DAG file, [**dagRun.py**](https://github.com/DEMaestro1/spark-flow-int/blob/main/dags/dagRun.py), which orchestrates the data pipeline tasks.
  2. The data transformation/processing script which uses Spark is located in [**transformationProcess.py**](https://github.com/DEMaestro1/spark-flow-int/blob/main/spark/tasks/transformationProcess.py)
  3. The script that loads the data to PostgreSQL can be found in [**loadProcess.py**](https://github.com/DEMaestro1/spark-flow-int/blob/main/spark/tasks/loadProcess.py)

## Scenario

The poverty data which can be found on https://data.worldbank.org/topic/poverty, contains poverty data for each county, for every year there has been a survey in said countries.

We are only looking for countries with a specific poverty level in the year of 2019. A quite simple scenario, more advanced transformations can be used for various other purposes.

## Base concepts

 - [ETL (Extract, Transform, Load)](https://en.wikipedia.org/wiki/Extract,_transform,_load)
 - [Pipeline](https://en.wikipedia.org/wiki/Pipeline_(computing))
 - [Apache Airflow](https://airflow.apache.org/docs/apache-airflow/stable/index.html) ([wikipedia page](https://en.wikipedia.org/wiki/Apache_Airflow))
 - [Apache Spark](https://spark.apache.org/docs/latest/)
 - [Airflow DAG](https://airflow.apache.org/docs/apache-airflow/stable/concepts.html#dags)
 - [PostgreSQL](https://www.postgresql.org/)

## Prerequisites
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/)

## Set-up

Download or pull the repo to your desired location.

You can change the user and password in docker-compose file if need be, make sure to change the configuration.conf file that is being used. Usually instead of user and pass being stored in such a way, projects use AWS Secrets or Azure Key Vault or various other ways.

## Installation

Start the installation with:

    docker build -t airflow-custom .
    docker-compose up -d

This command will pull and create Docker images and containers for Airflow as well as another PostgreSQL container to store poverty data.
This is done according to the instructions in the [docker-compose.yaml](https://github.com/DEMaestro1/spark-flow-int/blob/main/docker-compose.yaml) file:

After everything has been installed, you can check the status of your containers (if they are healthy) with:

    docker ps

**Note**: it might take up to 30 seconds for the containers to have the **healthy** flag after starting.

## Airflow Interface

You can now access the Airflow web interface by going to http://localhost:8080/. If you have not changed them in the docker-compose.yml file, the default user is **airflow** and password is **airflow**:

The defaults can be changed inside the docker-compose file.

After signing in, the Airflow home page is the DAGs list page. Here you will see all your DAGs and the Airflow example DAGs, sorted alphabetically. 

Any DAG python script saved in the directory [**dags/**](https://github.com/DEMaestro1/spark-flow-int/tree/main/dags), will show up on the DAGs page.

## Spark Interface

You can access the Spark driver by going to http://localhost:8090/. The port can be changed as needed in the docker-compose file.

## Pipeline Task by Task

#### Task `transformation_job`

The csv contains unnecessary data for our particular case and thus needs to be filtered out. We are using a SparkSubmitOperator to run the spark code in this case.

This runs the the transformationProcess.py file under the spark/tasks folder which selects a subset of the data that is required and filters it based on our use case.

The data is then written to the files folder as a parquet, ready to be loaded into a database.

#### Task `load_job`

The parquet is then read and loaded into the poverty table inside the postgres-db container, the spark code for this can be found under loadProcess.py file located under the spark/tasks.

The postgres jar file located under spark/jars is used for this task. The location of the jar is referenced under the SparkSubmitOperator.

The processed data is loaded into PostgreSQL instance running inside the container postgres-db, please be aware that a separate container named 'postgres' is being used by airflow and thus was not used for storing the processed data.

However if need be, the data can be stored on the same container but it is generally considered good practice to maintain separate containers for similar use cases.

To confirm if the data has been loaded as intended, you can run the following command:-

  docker exec -it spark-flow-int-postgres-db-1 psql -U user -d poverty -c "SELECT * FROM poverty"

## Shut Down and Restart Airflow

For any changes made in the configuration files to be applied, you will need to rebuild the Airflow images with the commands:
	
    docker build -t airflow-custom .
    docker-compose build

Recreate all the containers with:

    docker-compose up -d

## License
You can check out the full license [here](https://github.com/DEMaestro1/spark-flow-int/blob/main/LICENSE)

This project is licensed under the terms of the **MIT** license.
