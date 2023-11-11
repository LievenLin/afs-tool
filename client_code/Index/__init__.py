from ._anvil_designer import IndexTemplate
from anvil import *
import anvil.server

class Index(IndexTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    self.drop_down_1.items = anvil.server.call('get_supported_regions')
    self.drop_down_1.placeholder = anvil.server.call('get_supported_regions')[0]
    self.drop_down_2.items = ['OneFS 9.6', 'OneFS 9.7']
    self.drop_down_3.items = ['1-year', '3-years']
    self.drop_down_4.items = anvil.server.call('get_supported_instance_types',self.drop_down_1.selected_value)
    #self.drop_down_4.items = self.show_supported_instance_types()
    self.drop_down_5.items = ['gp3', 'st1']
    self.drop_down_6.items = anvil.server.call('get_supported_cluster_node_amount')
    self.drop_down_7.items = map(str, anvil.server.call('get_supported_node_disk_amount', self.drop_down_2.selected_value, self.drop_down_5.selected_value))
  
  # def show_supported_instance_types(self):
  #   supported_instance_types = anvil.server.call('get_supported_instance_types',self.drop_down_1.selected_value)
  #   return supported_instance_types
  
  def button_cal_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  def drop_down_1_change(self, **event_args):
    self.drop_down_4.items = anvil.server.call('get_supported_instance_types',self.drop_down_1.selected_value)

  def drop_down_2_change(self, **event_args):
    self.drop_down_4.items = anvil.server.call('get_supported_instance_types',self.drop_down_1.selected_value)
    self.drop_down_7.items = map(str, anvil.server.call('get_supported_node_disk_amount', self.drop_down_2.selected_value, self.drop_down_5.selected_value))
  
  def drop_down_5_change(self, **event_args):
    self.drop_down_7.items = map(str, anvil.server.call('get_supported_node_disk_amount', self.drop_down_2.selected_value, self.drop_down_5.selected_value))

  
