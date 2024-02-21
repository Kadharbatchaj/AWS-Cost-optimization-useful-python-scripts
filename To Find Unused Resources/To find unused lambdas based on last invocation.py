import boto3
import pandas as pd
from datetime import datetime, timedelta

# AWS regions to check
regions = ['us-east-1', 'us-east-2', 'ca-central-1']

def get_unused_lambdas(lambda_client, region):
    unused_lambdas_data = []
    
    # Get all Lambda functions in the specified region
    response = lambda_client.list_functions()
    
    # Iterate through each Lambda function
    for function in response['Functions']:
        function_name = function['FunctionName']
        
        # Get the last modified date of the Lambda function
        last_modified = function['LastModified']
        last_modified_date = datetime.strptime(last_modified[:19], "%Y-%m-%dT%H:%M:%S")
        
        # Calculate the age of the Lambda function
        age = datetime.now() - last_modified_date
        
        # Check if the Lambda function is older than a year and hasn't been invoked
        if age > timedelta(days=365):
            response_invocations = lambda_client.get_function_metric_data(
                FunctionName=function_name,
                MetricName='Invocations',
                StartTime=(datetime.now() - timedelta(days=365)).isoformat(),
                EndTime=datetime.now().isoformat(),
                Period=86400  # 1 day in seconds
            )
            if not response_invocations['MetricDataResults']:
                unused_lambdas_data.append({
                    'Region': region,
                    'LambdaName': function_name,
                    'LastInvocationTime': last_modified_date  # Store as datetime object
                })
    
    return unused_lambdas_data

# Create an empty DataFrame to store the data
result_df = pd.DataFrame(columns=['Region', 'LambdaName', 'LastInvocationTime'])

# Check unused lambdas for each region
for region in regions:
    session = boto3.Session(region_name=region)
    lambda_client = session.client('lambda')
    unused_lambdas = get_unused_lambdas(lambda_client, region)
    
    print(f"Unused Lambdas in {region}: {unused_lambdas}")  # Check if there are any unused Lambdas
    
    # Append the data to the DataFrame
    result_df = result_df.append(pd.DataFrame(unused_lambdas), ignore_index=True)

print(result_df)  # Print the DataFrame to check its contents

# Ensure LastInvocationTime is in datetime format
result_df['LastInvocationTime'] = pd.to_datetime(result_df['LastInvocationTime'])

# Convert LastInvocationTime to string format for Excel
result_df['LastInvocationTime'] = result_df['LastInvocationTime'].dt.strftime('%Y-%m-%d %H:%M:%S')

# Export to Excel
result_df.to_excel('unused_lambdas_info.xlsx', index=False)
print("Excel file generated successfully.")
