from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import sys

#Creating raw file path from passed system argument
fileLocation = sys.argv[1]
povertyData = f'{fileLocation}/PovertyData.csv'

spark = SparkSession \
    .builder \
    .appName('Spark-test') \
    .getOrCreate()
    
sc = spark.sparkContext
 
#Reading the csv and removing the first 4 lines from the file since it contains information regarding the data source.
rdd = sc.textFile(povertyData)\
            .zipWithIndex()\
            .filter(lambda x:x[1]>=4)\
            .map(lambda x:x[0])

#Converting the rdd into a dataframe.
df = spark.read.csv(rdd, header = True)
                 
#Selecting the columns required and filtering based on x criteria.                 
resultDf = df.select(col('Country Name').alias('Country_Name'),
                     col('Country Code').alias('Country_Code'),
                     col('2019').cast('float').alias('Stats_2019'))\
                    .filter(col('Stats_2019') > 1)

#Writing into a parquet file under the same location.                    
resultDf.write.format("parquet").mode('overwrite').save(f'{fileLocation}/processedData.parquet')
