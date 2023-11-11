import anvil.server
import os
import json

def load_json_data(path):
    f = open(path)
    data = json.load(f)
    f.close()
    return data

# get supported regions based on ec2 price json file
@anvil.server.callable
def get_supported_regions():
    # assume the price folder is under same dir with the costcal.py
    ec2_price_path = os.path.dirname(os.path.abspath(__file__)) + r"/price/ec2-price.json"
    data = load_json_data(ec2_price_path)
    supported_regions = [key for key in data]
    return supported_regions

# get supported instance type based on ec2 price json file and aws region inpu from users
def get_supported_instance_types(aws_region):
    # assume the price folder is under same dir with the costcal.py
    ec2_price_path = os.path.dirname(os.path.abspath(__file__)) + r"/price/ec2-price.json"
    data = load_json_data(ec2_price_path)
    supported_instance_types = [key for key in data[aws_region]]
    return supported_instance_types



def cal_ec2_instance_cost_hourly(aws_region, instance_amount, instance_type, payment_option):
    # assume the price folder is under same dir with the costcal.py
    ec2_price_path = os.path.dirname(os.path.abspath(__file__)) + r"/price/ec2-price.json"
    print(ec2_price_path)
    data = load_json_data(ec2_price_path)
    print(data)
    price = data[aws_region][instance_type][payment_option]
    total_cost_hourly = price * instance_amount
    return total_cost_hourly

def cal_ebs_cost_hourly(aws_region, ebs_type, capacity_gib):
    ebs_price_path = os.path.dirname(os.path.abspath(__file__)) + r"/price/ebs-price.json"
    data = load_json_data(ebs_price_path)
    price = data[aws_region][ebs_type]['capacity_price_hourly']
    total_cost_hourly = price * capacity_gib
    return total_cost_hourly



def cal_onefs_license_cost_monthly(contract_term, capacity_gib, onefs_license_discount):
    onefs_license_price_path = os.path.dirname(os.path.abspath(__file__)) + r"/price/onefs-license-price.json"
    f = open(onefs_license_price_path)
    data = json.load(f)
    f.close()
    if contract_term == '1-year':
        price = data[contract_term]['price']/12
    elif contract_term == '3-years':
        price = data[contract_term]['price']/36
    total_cost_monthly = price * capacity_gib * (1-onefs_license_discount/100)
    return total_cost_monthly

def cal_required_cluster_raw_capacity_tib(node_amount, node_disk_amount, node_disk_size):
    return node_amount * node_disk_amount * node_disk_size

def cal_onefs_aws_cost_monthly(aws_region, instance_type, disk_type, node_amount, node_disk_amount, node_disk_size, ec2_payment_option):
    ec2_instance_cost_monthly = 730 * cal_ec2_instance_cost_hourly(aws_region, node_amount, instance_type, ec2_payment_option)
    cluster_raw_capacity_gib = 1024 * cal_required_cluster_raw_capacity_tib(node_amount, node_disk_amount, node_disk_size)
    ebs_cost_monthly = 730 * cal_ebs_cost_hourly(aws_region, disk_type, cluster_raw_capacity_gib)
    onefs_aws_cost_monthly = ec2_instance_cost_monthly + ebs_cost_monthly
    return onefs_aws_cost_monthly

def cal_onefs_total_solution_cost_monthly(aws_region, onefs_term, onefs_license_discount, instance_type, disk_type, node_amount, node_disk_amount, node_disk_size, ec2_payment_option):
    onefs_aws_cost_monthly = cal_onefs_aws_cost_monthly(aws_region, instance_type, disk_type, node_amount, node_disk_amount, node_disk_size, ec2_payment_option)
    cluster_raw_capacity_gib = 1024 * cal_required_cluster_raw_capacity_tib(node_amount, node_disk_amount, node_disk_size)
    onefs_license_cost_monthly = cal_onefs_license_cost_monthly(onefs_term, cluster_raw_capacity_gib, onefs_license_discount)
    onefs_total_solution_cost_monthly = onefs_aws_cost_monthly + onefs_license_cost_monthly
    return onefs_total_solution_cost_monthly

# assume the protection level is 2n. 
# calculate the OneFS cluster usable capacity percentage based on protection overhead.
# e.g. for a 6 nodes cluster with default 2n protection level, the protection overhead is 33%, thus the available usable capacity is 67% of raw capacity
def cal_required_efs_capacity_tib(node_amount, node_disk_amount, node_disk_size, onefs_drr_ratio):
    if node_amount == 4:
        usable_perc = 0.50
    elif node_amount == 5:
        usable_perc = 0.60
    elif node_amount == 6:
        usable_perc = 0.67
    return node_amount * node_disk_amount * node_disk_size * usable_perc * onefs_drr_ratio

def cal_efs_cost_monthly(aws_region, storage_type, capacity_gib):
    efs_price_path = os.path.dirname(os.path.abspath(__file__)) + r"/price/efs-price.json"
    data = load_json_data(efs_price_path)
    price = data[aws_region][storage_type]["price"]
    total_cost_monthly = price * capacity_gib
    return total_cost_monthly

# calulate the EFS solution cost based on the cluster config. The methodology is based on the cluster raw capacity, protection overhead, and DRR ratio. 
def cal_efs_solution_cost_monthly(aws_region, storage_type, node_amount, node_disk_amount, node_disk_size, onefs_drr_ratio):
    efs_capacity_gib = 1024 * cal_required_efs_capacity_tib(node_amount, node_disk_amount, node_disk_size, onefs_drr_ratio)
    efs_solution_cost_monthly = cal_efs_cost_monthly(aws_region, storage_type, efs_capacity_gib)
    print(efs_capacity_gib)
    return efs_solution_cost_monthly
