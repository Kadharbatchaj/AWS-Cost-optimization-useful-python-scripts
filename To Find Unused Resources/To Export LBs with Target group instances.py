import boto3
import pandas as pd

def get_load_balancers_and_target_group_instances(regions):
    result = []

    for region in regions:
        elbv2 = boto3.client('elbv2', region_name=region)

        for lb in elbv2.describe_load_balancers()['LoadBalancers']:
            lb_dict = {
                'Region': region,
                'LoadBalancerName': lb['LoadBalancerName'],
                'TargetGroups': []
            }

            target_groups = elbv2.describe_target_groups(LoadBalancerArn=lb['LoadBalancerArn'])['TargetGroups']
            for tg in target_groups:
                tg_instances = []
                for instance in elbv2.describe_target_health(TargetGroupArn=tg['TargetGroupArn'])['TargetHealthDescriptions']:
                    tg_instances.append({
                        'InstanceId': instance['Target']['Id'],
                        'HealthStatus': instance['TargetHealth']['State']
                    })

                lb_dict['TargetGroups'].append({
                    'TargetGroupName': tg['TargetGroupName'],
                    'Instances': tg_instances
                })

            result.append(lb_dict)

    return result

if __name__ == '__main__':
    regions = ['us-east-1', 'us-east-2', 'ca-central-1']
    data = get_load_balancers_and_target_group_instances(regions)
    df = pd.DataFrame(data)
    df.to_excel('load_balancers_and_target_group_instances_3regions.xlsx', index=False)
