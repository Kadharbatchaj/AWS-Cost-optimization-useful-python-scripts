import boto3
import pandas as pd
from datetime import datetime, timedelta

def get_unused_queues():
    # Create an SQS client
    sqs_client = boto3.client('sqs')

    # Retrieve all queues
    response = sqs_client.list_queues()

    if 'QueueUrls' not in response:
        print('No queues found.')
        return []

    queue_urls = response['QueueUrls']
    unused_queues = []

    # Calculate the cutoff date (1 year ago)
    cutoff_date = datetime.now() - timedelta(days=365)

    # Iterate over each queue and check if it has any messages or has been modified after the cutoff date
    for queue_url in queue_urls:
        queue_attributes = sqs_client.get_queue_attributes(
            QueueUrl=queue_url,
            AttributeNames=['ApproximateNumberOfMessages', 'LastModifiedTimestamp']
        )

        approximate_number_of_messages = int(queue_attributes['Attributes']['ApproximateNumberOfMessages'])
        last_modified_timestamp = int(queue_attributes['Attributes']['LastModifiedTimestamp'])
        last_modified_datetime = datetime.fromtimestamp(last_modified_timestamp // 1000)  # Convert milliseconds to seconds

        if approximate_number_of_messages == 0 and last_modified_datetime < cutoff_date:
            unused_queues.append({
                'Queue URL': queue_url,
                'Last Used': 'Never'  # Default value for unused queues
            })
        else:
            # Get the timestamp of the last message sent or received for the queue
            response = sqs_client.receive_message(
                QueueUrl=queue_url,
                AttributeNames=['SentTimestamp'],
                MaxNumberOfMessages=1
            )

            messages = response.get('Messages', [])
            if messages:
                sent_timestamp = int(messages[0]['Attributes']['SentTimestamp'])
                last_used_datetime = datetime.fromtimestamp(sent_timestamp // 1000)  # Convert milliseconds to seconds
                unused_queues.append({
                    'Queue URL': queue_url,
                    'Last Used': last_used_datetime.strftime('%Y-%m-%d %H:%M:%S')
                })

    return unused_queues

# Get unused queues
unused_queues = get_unused_queues()

# Create a dataframe from the list of unused queues
df = pd.DataFrame(unused_queues)

# Export the dataframe to an Excel file
output_file = 'unused_queues.xlsx'
df.to_excel(output_file, index=False)
print(f'Successfully exported unused queues to {output_file}.')
