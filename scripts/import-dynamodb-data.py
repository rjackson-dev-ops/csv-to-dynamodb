import json
import boto3
import os
import csv
import codecs
import sys

s3 = boto3.resource('s3')
dynamodb = boto3.resource('dynamodb')

bucket = os.environ['bucket']
key = os.environ['key']
tableName = os.environ['table']

def lambda_handler():
  

   #get() does not store in memory
   try:
       obj = s3.Object(bucket, key).get()['Body']
   except Exception as e:
       print(e)
       print("S3 Object could not be opened. Check environment variable. ")
   try:
       table = dynamodb.Table(tableName)
   except Exception as e:
       print(e)
       print("Error loading DynamoDB table. Check if table was created correctly and environment variable.")

   batch_size = 100
   batch = []

   #DictReader is a generator; not stored in memory
   for row in csv.DictReader(codecs.getreader('utf-8')(obj)):


# ideas on fixing this issue
#https://stackoverflow.com/questions/11665628/read-data-from-csv-file-and-transform-from-string-to-correct-data-type-includin

      row['QuestionNumber'] = int(row['QuestionNumber'])
      row['NoEnergyImpact'] = int(row['NoEnergyImpact'])
      row['NoWealthImpact'] = int(row['NoWealthImpact'])
      row['YesEnergyImpact'] = int(row['YesEnergyImpact'])
      row['YesWealthImpact'] = int(row['YesWealthImpact'])

      if len(batch) >= batch_size:
         write_to_dynamo(batch)
         batch.clear()

      batch.append(row)

   if batch:
      write_to_dynamo(batch)

   return {
      'statusCode': 200,
      'body': json.dumps('Uploaded to DynamoDB Table')
   }

    
def write_to_dynamo(rows):
   try:
      table = dynamodb.Table(tableName)
   except Exception as e:
      print(e)
      print("Error loading DynamoDB table. Check if table was created correctly and environment variable.")

   try:
      with table.batch_writer() as batch:
         for i in range(len(rows)):
            batch.put_item(
               Item=rows[i]
            )
   except Exception as e:
      print(e)
      print("Error executing batch_writer")


if __name__ == '__main__':
    lambda_handler()
      