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
 
rdd = sc.textFile(povertyData)\
            .zipWithIndex()\
            .filter(lambda x:x[1]>=4)\
            .map(lambda x:x[0])

df = spark.read.csv(rdd, header = True)
                    
resultDf = df.select(col('Country Name').alias('Country_Name'),
                     col('Country Code').alias('Country_Code'),
                     col('2019').cast('float').alias('Stats_2019'))\
                    .filter(col('Stats_2019') > 1)
                    
resultDf.write.format("parquet").mode('overwrite').save(f'{fileLocation}/processedData.parquet')
