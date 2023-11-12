from ._anvil_designer import IndexTemplate
from anvil import *
import plotly.graph_objects as go
import anvil.server
from plotly import graph_objects as go
import plotly.express as px


class Index(IndexTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    
    self.drop_down_onefs_version.items = ['OneFS 9.6', 'OneFS 9.7']
    self.drop_down_onefs_term.items = ['1-year', '3-years']
    self.drop_down_region.items = anvil.server.call('get_supported_regions', self.drop_down_onefs_version.selected_value)
    self.drop_down_region.placeholder = self.drop_down_region.items[0]
    self.drop_down_instance_type.items = anvil.server.call('get_supported_instance_types', self.drop_down_onefs_version.selected_value, self.drop_down_region.selected_value)
    #self.drop_down_instance_type.items = self.show_supported_instance_types()
    self.drop_down_node_amount.items = map(str, anvil.server.call('get_supported_cluster_node_amount', self.drop_down_onefs_version.selected_value))
    self.drop_down_disk_type.items = ['gp3', 'st1']    
    self.drop_down_node_disk_amount.items = map(str, anvil.server.call('get_supported_node_disk_amount', self.drop_down_onefs_version.selected_value, self.drop_down_disk_type.selected_value))
    self.text_box_node_disk_size.placeholder = 4
    self.drop_down_payment_option.items = ['on-demand', 'saving-plan-3-years-no-upfront']
    self.drop_down_payment_option.placeholder = 'saving-plan-3-years-no-upfront'
  
  # def show_supported_instance_types(self):
  #   supported_instance_types = anvil.server.call('get_supported_instance_types',self.drop_down_region.selected_value)
  #   return supported_instance_types
  
  def button_cal_click(self, **event_args):
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

  def drop_down_region_change(self, **event_args):
    self.drop_down_instance_type.items = anvil.server.call('get_supported_instance_types', self.drop_down_onefs_version.selected_value, self.drop_down_region.selected_value)

  def drop_down_onefs_version_change(self, **event_args):
    self.drop_down_region.items = anvil.server.call('get_supported_regions', self.drop_down_onefs_version.selected_value)
    self.drop_down_instance_type.items = anvil.server.call('get_supported_instance_types', self.drop_down_onefs_version.selected_value, self.drop_down_region.selected_value)
    self.drop_down_node_amount.items = anvil.server.call('get_supported_cluster_node_amount', self.drop_down_onefs_version.selected_value)
    self.drop_down_node_disk_amount.items = map(str, anvil.server.call('get_supported_node_disk_amount', self.drop_down_onefs_version.selected_value, self.drop_down_disk_type.selected_value))
  
  def drop_down_disk_type_change(self, **event_args):
    self.drop_down_node_disk_amount.items = map(str, anvil.server.call('get_supported_node_disk_amount', self.drop_down_onefs_version.selected_value, self.drop_down_disk_type.selected_value))

  
