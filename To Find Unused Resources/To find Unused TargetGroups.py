import boto3
import pandas as pd

def get_target_groups_and_load_balancers():
    client = boto3.client('elbv2')  # Create a client for Elastic Load Balancing

    # Get all target groups
    target_groups_response = client.describe_target_groups()
    target_groups = target_groups_response['TargetGroups']

    # Get all load balancers
    load_balancers_response = client.describe_load_balancers()
    load_balancers = load_balancers_response['LoadBalancers']

    # Create a dictionary to store target groups and associated load balancers
    target_group_details = {}

    # Extract load balancer ARNs associated with each target group
    for tg in target_groups:
        target_group_arn = tg['TargetGroupArn']
        target_group_name = tg['TargetGroupName']
        target_group_details[target_group_arn] = {'TargetGroupName': target_group_name, 'LoadBalancers': []}

    for lb in load_balancers:
        lb_arn = lb['LoadBalancerArn']
        listeners = client.describe_listeners(LoadBalancerArn=lb_arn)['Listeners']
        for listener in listeners:
            if 'DefaultActions' in listener:
                for action in listener['DefaultActions']:
                    if 'TargetGroupArn' in action:
                        target_group_arn = action['TargetGroupArn']
                        if target_group_arn in target_group_details:
                            target_group_details[target_group_arn]['LoadBalancers'].append(lb_arn)

    return target_group_details

# Get target groups and load balancer associations
target_groups_info = get_target_groups_and_load_balancers()

# Prepare data for DataFrame
target_group_data = []

for tg_arn, tg_info in target_groups_info.items():
    if not tg_info['LoadBalancers']:
        tg_info['Status'] = 'Unused'
    else:
        tg_info['Status'] = 'Used'

    target_group_data.append({
        'TargetGroupName': tg_info['TargetGroupName'],
        'TargetGroupArn': tg_arn,
        'Status': tg_info['Status'],
        'LoadBalancers': ', '.join(tg_info['LoadBalancers']) if tg_info['LoadBalancers'] else 'N/A'
    })

# Create a Pandas DataFrame
df = pd.DataFrame(target_group_data)

# Export the DataFrame to an Excel file
excel_file = 'target_group_details.xlsx'
df.to_excel(excel_file, index=False)
print(f"Target group details exported to '{excel_file}'")
