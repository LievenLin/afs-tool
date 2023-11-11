import tcocal.costcal as costcal
import os


# hard coded for now
def get_supported_cluster_node_amount():
    return [4, 5, 6]

def get_supported_node_disk_amount(onefs_version, disk_type):
    supported_cluster_config_path = os.path.dirname(os.path.abspath(__file__)) + r"/price/supported_cluster_config.json"
    data = costcal.load_json_data(supported_cluster_config_path)
    supported_node_disk_amount = []
    if disk_type == 'gp3':
        supported_node_disk_amount =  data[onefs_version]['ssd-cluster']['supported-node-disk-amount']
    if disk_type == 'st1':
        supported_node_disk_amount =  data[onefs_version]['hdd-cluster']['supported-node-disk-amount']
    return supported_node_disk_amount


def get_supported_node_disk_size(onefs_version, disk_type):
    supported_cluster_config_path = os.path.dirname(os.path.abspath(__file__)) + r"/price/supported_cluster_config.json"
    data = costcal.load_json_data(supported_cluster_config_path)
    if disk_type == 'gp3':
        supported_node_disk_size_min =  data[onefs_version]['ssd-cluster']['supported-node-disk-size-min']
        supported_node_disk_size_max =  data[onefs_version]['ssd-cluster']['supported-node-disk-size-max']
        supported_node_disk_size_step =  data[onefs_version]['ssd-cluster']['supported-node-disk-size-step']
    if disk_type == 'st1':
        supported_node_disk_size_min =  data[onefs_version]['hdd-cluster']['supported-node-disk-size-min']
        supported_node_disk_size_max =  data[onefs_version]['hdd-cluster']['supported-node-disk-size-max']
        supported_node_disk_size_step =  data[onefs_version]['hdd-cluster']['supported-node-disk-size-step']
    supported_node_disk_size = [supported_node_disk_size_min, supported_node_disk_size_max, supported_node_disk_size_step]
    return supported_node_disk_size