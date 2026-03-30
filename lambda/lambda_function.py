### Function in AWS Lambda
import json
import pandas as pd
import boto3
import io
from datetime import datetime


def flatten(data):
    df = pd.json_normalize(data)
    return df


def lambda_handler(event, context):
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_name = event['Records'][0]['s3']['object']['key']
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=bucket_name, Key=file_name)
    content = response['Body'].read().decode('utf-8')
    data = json.loads(content)
    df = flatten(data)

    ###store in parquet
    parquet_buffer = io.BytesIO()
    df.to_parquet(parquet_buffer, index=False, engine='pyarrow')

    now = datetime.now()
    timestamp = now.strftime('%Y%m%d_%H%M%S')

    key_staging = f'output_datalake/ETL_output_{timestamp}.parquet'

    s3.put_object(Bucket=bucket_name, Key=key_staging, Body=parquet_buffer.getvalue())

    crawler_name = 'etl-pipeline-crawler-glue'
    glue = boto3.client('glue')
    response = glue.start_crawler(Name=crawler_name)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
