import anvil.server
import tcocal.costcal as costcal
import plotly.express as px
import pandas as pd



@anvil.server.callable
def init_comparison_figure():
  platforms = ['OneFS on AWS Annual Costs - USD', 'EFS Standard Storage Annual Costs - USD', 'EFS One Zone Storage Annual Costs - USD']
  annual_aws_ec2_cost = [0, 0, 0]
  annual_aws_storage_cost = [0, 0, 0]
  annual_license_cost = [0, 0, 0]
  wide_data = pd.DataFrame(
      {
          'Platforms': platforms,
          'Annual AWS Storage Cost - USD': annual_aws_storage_cost,
          'Annual AWS EC2 Cost - USD': annual_aws_ec2_cost,
          'Annual License Cost - USD': annual_license_cost
      }
  )
  
  wide_df = wide_data
  fig = px.bar(wide_df, x="Platforms", y=["Annual AWS Storage Cost - USD", "Annual AWS EC2 Cost - USD", "Annual License Cost - USD"], title="Annual Cost Compare to Amazon EFS", text_auto=True)
  return fig

@anvil.server.callable
def show_comparison_figure(aws_region, onefs_contract_term, onefs_license_discount, instance_type, disk_type, node_amount, node_disk_amount, node_disk_size, ec2_payment_option, onefs_drr_ratio):
    platforms = ['OneFS on AWS Annual Costs - USD', 'EFS Standard Storage Annual Costs - USD', 'EFS One Zone Storage Annual Costs - USD']
    annual_aws_ec2_cost = [0, 0, 0]
    annual_aws_storage_cost = [0, 0, 0]
    #annual_aws_cost = [0, 0, 0]
    annual_license_cost = [0, 0, 0]

    cluster_raw_capacity_gib = 1024 * costcal.cal_required_cluster_raw_capacity_tib(node_amount, node_disk_amount, node_disk_size)
    effective_capacity_tib = costcal.cal_required_efs_capacity_tib(node_amount, node_disk_amount, node_disk_size, onefs_drr_ratio)
    annual_aws_ec2_cost[0] = 12 * 730 * costcal.cal_ec2_instance_cost_hourly(aws_region, node_amount, instance_type, ec2_payment_option)
    annual_aws_storage_cost [0] = 12 * 730 * costcal.cal_ebs_cost_hourly(aws_region, disk_type, cluster_raw_capacity_gib)
    annual_license_cost[0] = 12 * costcal.cal_onefs_license_cost_monthly(onefs_contract_term, cluster_raw_capacity_gib, onefs_license_discount)
    data['OneFS on AWS'][0] = round(annual_aws_ec2_cost[0], 2)
    data['OneFS on AWS'][1] = round(annual_aws_storage_cost [0], 2)
    data['OneFS on AWS'][2] = round(annual_license_cost[0], 2)
    data['OneFS on AWS'][3] = round(annual_aws_ec2_cost[0] + annual_aws_storage_cost [0] + annual_license_cost[0], 2)
    data['OneFS on AWS'][4] = round(cluster_raw_capacity_gib, 2)
    data['OneFS on AWS'][5] = round(effective_capacity_tib, 2)
    data['OneFS on AWS'][6] = round((annual_aws_ec2_cost[0] + annual_aws_storage_cost [0] + annual_license_cost[0])/effective_capacity_tib, 2)

    
    print("cluster_raw_capacity_gib:")
    print(cluster_raw_capacity_gib)
    # Standard Storage EFS related cost
    annual_aws_storage_cost[1] = 12 * costcal.cal_efs_solution_cost_monthly(aws_region, "standard_storage", node_amount, node_disk_amount, node_disk_size, onefs_drr_ratio)
    annual_license_cost[1] = 0
    data['EFS Standard Storage'][1] = round(annual_aws_storage_cost[1], 2)
    data['EFS Standard Storage'][3] = round(annual_aws_storage_cost[1], 2)
    data['EFS Standard Storage'][5] = round(effective_capacity_tib, 2)
    data['EFS Standard Storage'][6] = round(annual_aws_storage_cost[1]/effective_capacity_tib, 2)

    # One Zone Storage EFS related cost
    annual_aws_storage_cost[2] = 12 * costcal.cal_efs_solution_cost_monthly(aws_region, "one_zone_storage", node_amount, node_disk_amount, node_disk_size, onefs_drr_ratio)
    annual_license_cost[2] = 0
    data['EFS One Zone Storage'][1] = round(annual_aws_storage_cost[2], 2)
    data['EFS One Zone Storage'][3] = round(annual_aws_storage_cost[2], 2)
    data['EFS One Zone Storage'][5] = round(effective_capacity_tib, 2)
    data['EFS One Zone Storage'][6] = round(annual_aws_storage_cost[2]/effective_capacity_tib, 2)

    print(annual_aws_storage_cost)
    print(annual_license_cost)
    
    # prepare data for result figure
    wide_data = pd.DataFrame({'Platforms': platforms,                            
                        'Annual AWS Storage Cost - USD': annual_aws_storage_cost,
                        'Annual AWS EC2 Cost - USD': annual_aws_ec2_cost,
                        'Annual License Cost - USD': annual_license_cost})

    fig = px.bar(wide_data, x="Platforms", y=["Annual AWS Storage Cost - USD", "Annual AWS EC2 Cost - USD", "Annual License Cost - USD"], title="Annual Cost Compare to Amazon EFS", text_auto=True, height=600)
    print(datetime.datetime.now())
    
    return fig