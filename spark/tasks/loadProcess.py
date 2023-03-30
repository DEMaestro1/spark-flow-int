import configparser
from pyspark.sql import SparkSession
import sys

#Grabbing arguments passed by airflow
fileLocation = sys.argv[1]
postgresURL = sys.argv[2]
postgresUser = sys.argv[3]
postgresPass = sys.argv[4]

stagedFileLocation = f'{fileLocation}/processedData.parquet'

#Creating Spark Session
spark = SparkSession \
    .builder \
    .appName('Spark-test') \
    .getOrCreate()
    

df = spark.read.parquet(stagedFileLocation)

df.write.format("jdbc")\
  .option("url", postgresURL)\
  .option("dbtable", "poverty")\
  .option("user", postgresUser)\
  .option("password", postgresPass)\
  .mode("overwrite")\
  .save()
    
 