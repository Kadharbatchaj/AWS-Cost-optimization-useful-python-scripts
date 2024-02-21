import boto3
import pandas as pd
from datetime import datetime

def find_empty_buckets():
    s3 = boto3.client("s3")
    empty_buckets = []
    errored_buckets = []

    result = s3.list_buckets()
    for bucket in result["Buckets"]:
        try:
            region = s3.get_bucket_location(Bucket=bucket["Name"])['LocationConstraint']
            if region is None:
                region = 'us-east-1'  # Default region if location is not specified

            contents = s3.list_objects_v2(Bucket=bucket["Name"])
            if 'KeyCount' not in contents or contents['KeyCount'] == 0:
                creation_date = bucket["CreationDate"]
                creation_date_str = creation_date.strftime("%Y-%m-%d %H:%M:%S")
                empty_buckets.append({'Bucket Name': bucket["Name"], 'Region': region, 'Creation Date': creation_date_str})
            else:
                errored_buckets.append({'Bucket Name': bucket["Name"], 'Error': 'Bucket not empty'})
        except Exception as e:
            errored_buckets.append({'Bucket Name': bucket["Name"], 'Error': str(e)})

    df_empty = pd.DataFrame(empty_buckets)
    df_errored = pd.DataFrame(errored_buckets)

    with pd.ExcelWriter("bucket_details.xlsx") as writer:
        df_empty.to_excel(writer, sheet_name='Empty Buckets', index=False)
        df_errored.to_excel(writer, sheet_name='Errored Buckets', index=False)

if __name__ == '__main__':
    find_empty_buckets()
