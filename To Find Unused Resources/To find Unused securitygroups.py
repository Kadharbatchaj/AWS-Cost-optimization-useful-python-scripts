import boto3
import pandas as pd

def get_vpc_name(vpc_id, ec2_client):
    response = ec2_client.describe_vpcs(VpcIds=[vpc_id])
    vpc = response['Vpcs'][0]
    tags = vpc.get('Tags', [])
    for tag in tags:
        if tag['Key'] == 'Name':
            return tag['Value']
    return ''

def get_unused_security_groups():
    regions = ['us-east-1', 'us-east-2', 'ca-central-1']
    combined_unused_sgs = []

    for region in regions:
        ec2_client = boto3.client('ec2', region_name=region)
        rds_client = boto3.client('rds', region_name=region)
        documentdb_client = boto3.client('docdb', region_name=region)
        redshift_client = boto3.client('redshift', region_name=region)
        elasticache_client = boto3.client('elasticache', region_name=region)
        es_client = boto3.client('es', region_name=region)

        # Fetching EC2 instances
        ec2_response = ec2_client.describe_instances()
        ec2_instances = ec2_response['Reservations']
        used_security_groups = set()
        for reservation in ec2_instances:
            for instance in reservation['Instances']:
                for sg in instance['SecurityGroups']:
                    used_security_groups.add(sg['GroupId'])

        # Fetching ENIs
        eni_response = ec2_client.describe_network_interfaces()
        enis = eni_response['NetworkInterfaces']
        for eni in enis:
            for sg in eni['Groups']:
                used_security_groups.add(sg['GroupId'])

        # Fetching RDS instances
        rds_response = rds_client.describe_db_instances()
        rds_instances = rds_response['DBInstances']
        for rds_instance in rds_instances:
            for sg in rds_instance['VpcSecurityGroups']:
                used_security_groups.add(sg['VpcSecurityGroupId'])

        # Fetching DocumentDB clusters
        documentdb_response = documentdb_client.describe_db_clusters()
        documentdb_clusters = documentdb_response['DBClusters']
        for docdb_cluster in documentdb_clusters:
            for sg in docdb_cluster['VpcSecurityGroups']:
                used_security_groups.add(sg['VpcSecurityGroupId'])

        # Fetching Redshift clusters
        redshift_response = redshift_client.describe_clusters()
        redshift_clusters = redshift_response['Clusters']
        for redshift_cluster in redshift_clusters:
            for sg in redshift_cluster['VpcSecurityGroups']:
                used_security_groups.add(sg['VpcSecurityGroupId'])

        # Fetching Elastic Cache clusters
        elasticache_response = elasticache_client.describe_cache_clusters()
        elasticache_clusters = elasticache_response['CacheClusters']
        for elasticache_cluster in elasticache_clusters:
            for sg in elasticache_cluster['SecurityGroups']:
                used_security_groups.add(sg['SecurityGroupId'])

        # Fetching Elasticsearch domains
        es_response = es_client.list_domain_names()
        es_domains = es_response['DomainNames']
        for es_domain in es_domains:
            es_domain_response = es_client.describe_elasticsearch_domain(
                DomainName=es_domain['DomainName']
            )
            if 'VPCOptions' in es_domain_response['DomainStatus']:
                for sg in es_domain_response['DomainStatus']['VPCOptions']['SecurityGroupIds']:
                    used_security_groups.add(sg)

        # Fetching all security groups in the region
        sg_response = ec2_client.describe_security_groups()
        all_security_groups = sg_response['SecurityGroups']

        # Finding unused security groups in the region
        for sg in all_security_groups:
            if sg['GroupId'] not in used_security_groups:
                vpc_name = get_vpc_name(sg['VpcId'], ec2_client)
                combined_unused_sgs.append({
                    'Region': region,
                    'SecurityGroupID': sg['GroupId'],
                    'SecurityGroupName': sg['GroupName'],
                    'VPCID': sg['VpcId'],
                    'VPCName': vpc_name
                })

    return combined_unused_sgs

# Calling the function to fetch unused security groups for specified regions
unused_sgs = get_unused_security_groups()

# Creating a pandas DataFrame from the list of unused security groups
df = pd.DataFrame(unused_sgs)

# Reordering the columns
df = df[['Region', 'SecurityGroupID', 'SecurityGroupName', 'VPCID', 'VPCName']]

# Saving the DataFrame to an Excel file
df.to_excel('combined_unused_security_groups_3regions-latest.xlsx', index=False)

print("Unused Security Groups exported to combined_unused_security_groups.xlsx")
