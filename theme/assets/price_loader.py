import requests, os
import boto3
import costcal 
import json

def load_json_file(path):
    f = open(path)
    data = json.load(f)
    f.close()
    return data

# https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/fetching-price-list-manually-step-1.html
# Finding available AWS services, needed service code: AmazonEC2, AmazonEFS, and AmazonFSx
def download_aws_service_index():
    aws_service_index_url = 'https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/index.json'
    aws_service_index_path = os.path.dirname(os.path.abspath(__file__)) + r"/price/service_index.json" 
    is_downloaded = False
    response = requests.get(aws_service_index_url)

    if response.status_code == 200:
        with open(aws_service_index_path, 'wb') as file:
            file.write(response.content)
        is_downloaded = True
        print(f"Downloaded '{aws_service_index_url}' to '{aws_service_index_path}'")
    else:
        print(f"Failed to download '{aws_service_index_url}'. Status code: {response.status_code}")
    return is_downloaded

def filter_aws_service_index_json(aws_service_index_path, filter):

    filtered_aws_service_index_json = {
        "formatVersion" : "",
        "disclaimer" : "",
        "publicationDate" : "",
        "offers" : {}
    }

    aws_service_index_json = load_json_file(aws_service_index_path)
    filtered_aws_service_index_json["formatVersion"] = aws_service_index_json["formatVersion"]
    filtered_aws_service_index_json["disclaimer"] = aws_service_index_json["disclaimer"]
    filtered_aws_service_index_json["publicationDate"] = aws_service_index_json["publicationDate"]
    for key in aws_service_index_json["offers"].keys():
        if key in filter:
           filtered_aws_service_index_json["offers"][key] = aws_service_index_json["offers"][key]
    
    return json.dumps(filtered_aws_service_index_json)

def get_service_current_version_index_url(aws_service_index_path, offer_code):
    aws_service_index_json = load_json_file(aws_service_index_path)
    service_current_version_index_url = aws_service_index_json["offers"][offer_code]["currentVersionUrl"]
    return service_current_version_index_url

# for service that has saving plan available, e.g. AmamzonEC2
def get_service_current_savingsplan_index_url(aws_service_index_path, offer_code):
    aws_service_index_json = load_json_file(aws_service_index_path)
    service_current_savingsplan_index_url = aws_service_index_json["offers"][offer_code]["currentSavingsPlanIndexUrl"]
    return service_current_savingsplan_index_url
    
# Download a specific service index json file for all regions
# Please notet that this index json file may 5GiB+
def download_service_current_version_index(aws_service_index_path, offer_code):
    pricing_endpoint = "https://pricing.us-east-1.amazonaws.com"
    service_current_version_index_url = pricing_endpoint + get_service_current_version_index_url(aws_service_index_path, offer_code)
    service_current_version_index_path = os.path.dirname(os.path.abspath(__file__)) + r"/price/" + offer_code + "_current_version_index.json"
    #service_current_version_index_path = r"C:\vscode\psve-tco\tcocal" + r"/price/" + offer_code + "_current_version_index.json"
    is_downloaded = False
    response = requests.get(service_current_version_index_url)

    if response.status_code == 200:
        with open(service_current_version_index_path, 'wb') as file:
            file.write(response.content)
        is_downloaded = True
        print(f"Downloaded '{service_current_version_index_path}' to '{service_current_version_index_path}'")
    else:
        print(f"Failed to download '{service_current_version_index_path}'. Status code: {response.status_code}")
    return is_downloaded


def filter_ec2_service_json(service_current_version_index_path, filter):
    return 1

# query a specific instance type price info for all regions of on-demand
def query_instance_type_price_list_on_demand(instance_type):
    client = boto3.client('pricing')
    ec2_price_list = {
        "PriceList": []
    }

    response = client.get_products(
        ServiceCode='AmazonEC2', 
        Filters=[
            {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': instance_type},
            {'Type': 'TERM_MATCH', 'Field': 'operatingSystem', 'Value': 'Linux'},
            {'Type': 'TERM_MATCH', 'Field': 'tenancy', 'Value': 'Shared'},
            #{'Type': 'TERM_MATCH', 'Field': 'regionCode', 'Value': 'us-west-2'},
            {'Type': 'TERM_MATCH', 'Field': 'preInstalledSw', 'Value': 'NA'},         
        ],
        MaxResults=100,
    )
   
    for price_list in response['PriceList']:
        price_list_json = json.loads(price_list)
        if "instancesku" in price_list_json["product"]["attributes"]:
            #print(price_list_json["product"]["attributes"]["instancesku"])
            #print(price_list_json["product"]["sku"])
            continue
        else:
            print("found on demand instance price")
            print(price_list_json["product"]["attributes"]["regionCode"])
            print(price_list_json["product"]["sku"])
            ec2_price_list["PriceList"].append(price_list_json)

    return ec2_price_list

# Save a set of instance types price info to a json file
# used for saving supported instance types original price info
def generate_supported_ec2_price_json_file(instance_types):
    #ec2_price_json_path = os.path.dirname(os.path.abspath(__file__)) + r"/price/{}-on-demand-price.json".format(instance_type)
    #ec2_price_json_path = r"C:\vscode\psve-tco\tcocal" + "/price/{}-on-demand-price.json".format(instance_type)
    ec2_price_json_path = r"C:\vscode\psve-tco\tcocal" + "/price/supported-instance-types-on-demand-price.json"
    ec2_price_list = {
        "PriceList": []
    }
    for instance_type in instance_types:
        instance_type_price_list = query_instance_type_price_list_on_demand(instance_type)
        ec2_price_list["PriceList"] = ec2_price_list["PriceList"] + instance_type_price_list["PriceList"]
    
    print(len(ec2_price_list["PriceList"]))
    #print(ec2_price_list)
    f = open(ec2_price_json_path, 'w')
    json.dump(ec2_price_list, f)
    f.close()

# query a specific ebs type price info for all regions, not include IOPS/throughput price
# product_family = 'Storage' for capacity price
# product_family = 'System Operation' for IOPS and throughput price, at least for gp3, not validate for others
def query_ebs_price_list(volume_api_name, product_family):
    client = boto3.client('pricing')
    ebs_price_list = {
        "PriceList": []
    }
    response = client.get_products(
        ServiceCode='AmazonEC2', 
        Filters=[
            {'Type': 'TERM_MATCH', 'Field': 'volumeApiName', 'Value': volume_api_name},
            #{'Type': 'TERM_MATCH', 'Field': 'regionCode', 'Value': 'us-west-2'},
            {'Type': 'TERM_MATCH', 'Field': 'productFamily', 'Value': product_family},  
            #{'Type': 'TERM_MATCH', 'Field': 'productFamily', 'Value': 'System Operation'}, 
        ],
        MaxResults=100,
    )
    #print(response)
    #ebs_price_list["PriceList"] = ebs_price_list["PriceList"] + response["PriceList"]
    for price_list in response['PriceList']:  
        ebs_price_list["PriceList"].append(json.loads(price_list))
    while ("NextToken" in response.keys()):
        next_token = response["NextToken"]
        response = client.get_products(
            ServiceCode='AmazonEC2', 
            Filters=[
                {'Type': 'TERM_MATCH', 'Field': 'volumeApiName', 'Value': volume_api_name},
                #{'Type': 'TERM_MATCH', 'Field': 'regionCode', 'Value': 'us-west-2'},
                {'Type': 'TERM_MATCH', 'Field': 'productFamily', 'Value': product_family},  
                #{'Type': 'TERM_MATCH', 'Field': 'productFamily', 'Value': 'System Operation'},  
            ],
            MaxResults=100,
            NextToken=next_token,
        )
        #ebs_price_list["PriceList"] = ebs_price_list["PriceList"] + response["PriceList"]
        for price_list in response['PriceList']:  
            ebs_price_list["PriceList"].append(json.loads(price_list))
    print(len(ebs_price_list["PriceList"]))    
    return ebs_price_list

# Save a set of EBS volume price info to a json file
# used for saving supported EBS types original price info
def generate_supported_ebs_price_json_file(volume_api_names, product_family):
    #ebs_price_json_path = os.path.dirname(os.path.abspath(__file__)) + r"/price/{}-on-demand-price.json".format(instance_type)
    #ebs_price_json_path = r"C:\vscode\psve-tco\tcocal" + "/price/{}-on-demand-price.json".format(instance_type)
    if product_family == "Storage":
        ebs_price_json_path = r"C:\vscode\psve-tco\tcocal" + "/price/supported-ebs-capacity-price.json"
    elif product_family == "System Operation":
        ebs_price_json_path = r"C:\vscode\psve-tco\tcocal" + "/price/supported-ebs-perf-price.json"
    ebs_price_list = {
        "PriceList": []
    }
    for volume_api_name in volume_api_names:
        volume_api_name_price_list = query_ebs_price_list(volume_api_name, product_family)
        ebs_price_list["PriceList"] = ebs_price_list["PriceList"] + volume_api_name_price_list["PriceList"]
    
    print(len(ebs_price_list["PriceList"]))
    #print(ebs_price_list)
    f = open(ebs_price_json_path, 'w')
    json.dump(ebs_price_list, f)
    f.close()

# Query AWS EFS service price list, including all regions and provisioned throughput
def query_efs_price_list():
    client = boto3.client('pricing')
    efs_price_list = {
        "PriceList": []
    }
    response = client.get_products(
        ServiceCode='AmazonEFS', 
        Filters=[
            #{'Type': 'TERM_MATCH', 'Field': 'volumeApiName', 'Value': volume_api_name},
            #{'Type': 'TERM_MATCH', 'Field': 'regionCode', 'Value': 'us-west-2'},
            #{'Type': 'TERM_MATCH', 'Field': 'productFamily', 'Value': product_family},  
            #{'Type': 'TERM_MATCH', 'Field': 'productFamily', 'Value': 'System Operation'}, 
        ],
        MaxResults=100,
    )
    #print(response)
    #ebs_price_list["PriceList"] = ebs_price_list["PriceList"] + response["PriceList"]
    for price_list in response['PriceList']:  
        efs_price_list["PriceList"].append(json.loads(price_list))
    while ("NextToken" in response.keys()):
        next_token = response["NextToken"]
        response = client.get_products(
            ServiceCode='AmazonEFS', 
            Filters=[
                #{'Type': 'TERM_MATCH', 'Field': 'volumeApiName', 'Value': volume_api_name},
                #{'Type': 'TERM_MATCH', 'Field': 'regionCode', 'Value': 'us-west-2'},
                #{'Type': 'TERM_MATCH', 'Field': 'productFamily', 'Value': product_family},  
                #{'Type': 'TERM_MATCH', 'Field': 'productFamily', 'Value': 'System Operation'},  
            ],
            MaxResults=100,
            NextToken=next_token,
        )
        #ebs_price_list["PriceList"] = ebs_price_list["PriceList"] + response["PriceList"]
        for price_list in response['PriceList']:  
            efs_price_list["PriceList"].append(json.loads(price_list))
    print(len(efs_price_list["PriceList"]))    
    return efs_price_list

# Save AWS EFS original price info to a json file
def generate_efs_price_json_file():
    #ebs_price_json_path = os.path.dirname(os.path.abspath(__file__)) + r"/price/{}-on-demand-price.json".format(instance_type)
    #ebs_price_json_path = r"C:\vscode\psve-tco\tcocal" + "/price/{}-on-demand-price.json".format(instance_type)
    efs_price_json_path = r"C:\vscode\psve-tco\tcocal" + "/price/efs-price-original.json"    
    efs_price_list = query_efs_price_list()
    
    print(len(efs_price_list["PriceList"]))
    #print(ebs_price_list)
    f = open(efs_price_json_path, 'w')
    json.dump(efs_price_list, f)
    f.close()

generate_efs_price_json_file()
#volume_api_name = "st1"
volume_api_names = ["gp3", "st1"]
product_family = "Storage"
generate_supported_ebs_price_json_file(volume_api_names, product_family)
product_family = "System Operation"
generate_supported_ebs_price_json_file(volume_api_names, product_family)
ebs_price_list = query_ebs_price_list(volume_api_name)


supported_instance_types = ["m5dn.8xlarge", "m5d.24xlarge"]
generate_supported_ec2_price_json_file(supported_instance_types)



aws_service_index_path = r"C:\vscode\psve-tco\tcocal\price\service_index.json" 
offer_code = "AmazonEC2"
filter = ["AmazonEC2", "AmazonEFS" ]
filtered_aws_service_index_json = filter_aws_service_index_json(aws_service_index_path, filter)
download_service_current_version_index(aws_service_index_path, offer_code)

client = boto3.client('pricing')
response = client.get_products(
    ServiceCode='AmazonEC2',
    Filters=[
        {
            'Field': 'ServiceCode',
            'Type': 'TERM_MATCH',
            'Value': 'AmazonEC2',
        },
        {
            # 'Field': 'volumeType',
            'Field': 'volumeApiName',
            'Type': 'TERM_MATCH',
            'Value': 'gp3',
        },
        {
            # 'Field': 'volumeType',
            'Field': 'regionCode',
            'Type': 'TERM_MATCH',
            'Value': 'us-east-1',
        },
    ],
    FormatVersion='aws_v1',
    MaxResults=20,
)

client = boto3.client('pricing')
response = client.get_products(
    ServiceCode='AmazonEC2', 
    Filters=[
        {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': 'm5dn.8xlarge'},
        {'Type': 'TERM_MATCH', 'Field': 'operatingSystem', 'Value': 'Linux'},
        {'Type': 'TERM_MATCH', 'Field': 'tenancy', 'Value': 'Shared'},
        #{'Type': 'TERM_MATCH', 'Field': 'regionCode', 'Value': 'us-west-2'},
        {'Type': 'TERM_MATCH', 'Field': 'preInstalledSw', 'Value': 'NA'},         
    ],
    MaxResults=100,
)
#for i in (0, len(response['PriceList'])):

ec2_price_list = []

for price_list in response['PriceList']:
    price_list_json = json.loads(price_list)
    if "instancesku" in price_list_json["product"]["attributes"]:
       #print(price_list_json["product"]["attributes"]["instancesku"])
       #print(price_list_json["product"]["sku"])
       continue
    else:
       print("found on demand instance price")
       print(price_list_json["product"]["attributes"]["regionCode"])
       print(price_list_json["product"]["sku"])
       ec2_price_list.append(price_list)

len(ec2_price_list)

print(response)
print(response['PriceList'][0])
print(len(response['PriceList']))

response = client.get_attribute_values(
    AttributeName='volumeApiName',
    MaxResults=20,
    ServiceCode='AmazonEC2',
)

print(response)



# Initialize the AWS Price List client
pricing = boto3.client('pricing', region_name='us-east-1')

# Define the parameters for the pricing API request
service_code = 'AmazonEC2'  # Service code for EC2
instance_type = 'm5dn.24xlarege'  # Replace with the desired EC2 instance type

# Get the pricing information for the instance type
response = pricing.get_products(ServiceCode=service_code, Filters=[
    {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': instance_type}
])

# Extract and print the list of supported regions
for product in response['PriceList']:
    product = json.loads(product)
    supported_regions = product['product']['attributes']['location']
    print(f"Supported regions for {instance_type}: {supported_regions}")


client = boto3.client('pricing')
response = client.get_products(
    ServiceCode='AmazonEC2', 
    Filters=[
        #{'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': 'm5dn.8xlarge'},
        # {'Type': 'TERM_MATCH', 'Field': 'operatingSystem', 'Value': 'Linux'},
        # {'Type': 'TERM_MATCH', 'Field': 'tenancy', 'Value': 'Shared'},
        #{'Type': 'TERM_MATCH', 'Field': 'regionCode', 'Value': 'us-west-2'},
        # {'Type': 'TERM_MATCH', 'Field': 'preInstalledSw', 'Value': 'NA'},    
        {'Type': 'TERM_MATCH', 'Field': 'productFamily', 'Value': 'Savings Plans'},
    ],
    MaxResults=100,
)
for price_list in response['PriceList']:  
    price_list_json = json.loads(price_list)
    print(price_list_json["product"]["productFamily"])

    if price_list_json["product"]["productFamily"] == "Storage":
        print(price_list_json["product"]["attributes"]["storageClass"])

client = boto3.client('savingsplans')

if __name__ == '__main__':
    pass