#import logging
import json
from pyspark.sql import SparkSession
from pyspark.sql.types import *
import pyspark.sql.functions as psf


# TODO Create a schema for incoming resources
schema = StructType([StructField("crime_id", StringType(), True),
                     StructField("original_crime_type_name", StringType(), True),
                     StructField("report_date", StringType(), True),
                     StructField("call_date", StringType(), True),
                     StructField("offense_date", StringType(), True),
                     StructField("call_time", StringType(), True),
                     StructField("call_date_time", StringType(), True),
                     StructField("disposition", StringType(), True),
                     StructField("address", StringType(), True),
                     StructField("city", StringType(), True),
                     StructField("state", StringType(), True),
                     StructField("agency_id", StringType(), True),
                     StructField("address_type", StringType(), True),
                     StructField("common_location", StringType(), True)
                     ])

def run_spark_job(spark):

    # TODO Create Spark Configuration
    # Create Spark configurations with max offset of 200 per trigger
    # set up correct bootstrap server and port
    df = spark \
        .readStream \
        .format('kafka'
        ).option('kafka.bootstrap.servers', 'localhost:9092'
        ).option('subscribe', 'udacity.project2.police.calls'
        ).option('startingOffsets', 'earliest'
        ).option('maxOffsetsPerTrigger', 200
        ).option("stopGracefullyOnShutdown", "true"
        ).load()

    # Show schema for the incoming resources for checks
    df.printSchema()

    # TODO extract the correct column from the kafka input resources
    # Take only value and convert it to String
    kafka_df = df.selectExpr("CAST(value AS STRING)")

    service_table = kafka_df\
        .select(psf.from_json(psf.col('value'), schema).alias("DF"))\
        .select("DF.*")
    #query = service_table.writeStream.outputMode("append").format("console").start()
    # TODO select original_crime_type_name and disposition
    distinct_table = service_table.selectExpr('original_crime_type_name', 'disposition', 'to_timestamp(call_date_time) as call_date_time').withWatermark("call_date_time", "60 minutes")

    # count the number of original crime type
    agg_df = distinct_table.withWatermark("call_date_time", "60 minutes"
                                  ).groupBy(psf.window(distinct_table.call_date_time, "60 minutes", "10 minutes"), distinct_table.original_crime_type_name
                                  ).count()

    # TODO Q1. Submit a screen shot of a batch ingestion of the aggregation
    # TODO write output stream
    query = agg_df.writeStream.format("console"
                                            ).outputMode("update"
                                            ).trigger(once=True#processingTime="30 seconds"
                                            ).start()
    
    # TODO attach a ProgressReporter
    query.awaitTermination()
    time.sleep(10)

    # TODO get the right radio code json path
    radio_code_json_filepath = "radio_code.json"
    radio_code_df = spark.read.json(radio_code_json_filepath, multiLine =True)

    # clean up your data so that the column names match on radio_code_df and agg_df
    # we will want to join on the disposition code
    agg_df = distinct_table.withWatermark("call_date_time", "60 minutes"
                                  ).groupBy(psf.window(distinct_table.call_date_time, "60 minutes", "10 minutes"), distinct_table.disposition
                                  ).count()

    # TODO rename disposition_code column to disposition
    radio_code_df = radio_code_df.withColumnRenamed("disposition_code", "disposition")

    # TODO join on disposition column
    join_query = agg_df.join(radio_code_df, 'disposition', 'left_outer')
    
    
    join_query.writeStream.format("console").outputMode("complete").start().awaitTermination()
    
    

if __name__ == "__main__":
    #logger = logging.getLogger(__name__)

    # TODO Create Spark in Standalone mode
    spark = SparkSession \
        .builder \
        .master("local[*]") \
        .appName("KafkaSparkStructuredStreaming") \
        .config("spark.ui.port", 3000) \
        .getOrCreate()

    #logger.info("Spark started")

    run_spark_job(spark)

    spark.stop()