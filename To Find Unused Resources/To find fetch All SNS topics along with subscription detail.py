import boto3
import pandas as pd

def get_all_sns_topics(regions):
    all_topics = []
    for region in regions:
        sns = boto3.client('sns', region_name=region)
        topics = sns.list_topics()['Topics']
        
        for topic in topics:
            topic_arn = topic['TopicArn']
            subscriptions = sns.list_subscriptions_by_topic(TopicArn=topic_arn)['Subscriptions']
            if not subscriptions:
                topic_data = {
                    'Region': region,
                    'Topic ARN': topic_arn,
                    'Protocol': 'No subscriptions found',
                    'Endpoint': 'No subscriptions found'
                }
                all_topics.append(topic_data)
            else:
                for sub in subscriptions:
                    topic_data = {
                        'Region': region,
                        'Topic ARN': topic_arn,
                        'Subscription ARN': sub['SubscriptionArn'],
                        'Protocol': sub['Protocol'],
                        'Endpoint': sub['Endpoint']
                    }
                    all_topics.append(topic_data)

    return all_topics

def main():
    regions = ['us-east-1', 'us-east-2', 'ca-central-1']
    all_topics = get_all_sns_topics(regions)

    df = pd.DataFrame(all_topics)
    filename = "sns_topics_with_subscriptions_details_Latest.xlsx"
    df.to_excel(filename, index=False)
    print(f"Data written to {filename}")

if __name__ == "__main__":
    main()
