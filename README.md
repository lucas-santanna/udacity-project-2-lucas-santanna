# udacity-project-2-lucas-santanna

<h2> Question 1 - How did changing values on the SparkSession property parameters affect the throughput and latency of the data? </h2>

The most option with the biggest impact was the processedRowsPerSecond and maxOffsetsPerTrigger. The bigger the values got, the fastest the application could process the incoming data rows from kafka. 

<h2> Question 2 - What were the 2-3 most efficient SparkSession property key/value pairs? Through testing multiple variations on values, how can you tell these were the most optimal? </h2>
  
Setting maxOffsetsPerTrigger and processedRowsPerSecond to 1000 had a huge impact in the data processing time. Combined with the setting spark.sql.shuffle.partitions set to 5, they were the optimal solution I could find.
