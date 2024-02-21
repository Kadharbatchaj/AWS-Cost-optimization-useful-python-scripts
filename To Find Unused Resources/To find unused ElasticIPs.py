import boto3

def get_unused_elastic_ips():
    # Initialize Boto3 clients for EC2
    ec2_client = boto3.client('ec2')

    # Get all Elastic IPs
    response = ec2_client.describe_addresses()
    elastic_ips = response['Addresses']

    # Find unused Elastic IPs
    unused_ips = []
    for ip in elastic_ips:
        if 'InstanceId' not in ip and 'NetworkInterfaceId' not in ip and 'NetworkLoadBalancerArn' not in ip and 'NatGatewayId' not in ip:
            unused_ips.append(ip['PublicIp'])

    return unused_ips

if __name__ == "__main__":
    unused_ips = get_unused_elastic_ips()
    print("Unused Elastic IPs:")
    for ip in unused_ips:
        print(ip)
