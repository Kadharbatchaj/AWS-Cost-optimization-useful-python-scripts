import boto3
import pandas as pd

def get_ecs_load_balancers():
    # Initialize Boto3 clients
    ecs_client = boto3.client('ecs')
    elbv2_client = boto3.client('elbv2')

    # Fetch ECS clusters
    ecs_clusters = ecs_client.list_clusters()['clusterArns']

    all_services = []

    for cluster_arn in ecs_clusters:
        # Paginate through ECS services in each cluster
        paginator = ecs_client.get_paginator('list_services')
        service_pages = paginator.paginate(cluster=cluster_arn)

        for page in service_pages:
            services = page['serviceArns']

            for service_arn in services:
                # Describe ECS service to get details
                service_details = ecs_client.describe_services(cluster=cluster_arn, services=[service_arn])['services'][0]
                service_name = service_details['serviceName']
                load_balancers = []

                # Fetch load balancers associated with the service
                for lb in service_details.get('loadBalancers', []):
                    lb_arn = lb['targetGroupArn']

                    # Describe the load balancer to get more details
                    lb_details = elbv2_client.describe_target_groups(TargetGroupArns=[lb_arn])['TargetGroups'][0]
                    lb_name = lb_details['TargetGroupName']

                    # Append load balancer details to the list
                    load_balancers.append({
                        'LoadBalancerName': lb_name,
                        'ECS Cluster': cluster_arn.split('/')[-1],
                        'ECS Service': service_name
                    })

                all_services.extend(load_balancers)

    return all_services

# Get ECS services and their associated load balancers
ecs_services = get_ecs_load_balancers()

# Convert the data into a DataFrame
df = pd.DataFrame(ecs_services)

# Write the DataFrame to an Excel file
excel_file = 'ecs_services_load_balancers.xlsx'
df.to_excel(excel_file, index=False)

print(f"Data written to {excel_file}")
