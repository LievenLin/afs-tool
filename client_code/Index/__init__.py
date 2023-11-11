from ._anvil_designer import IndexTemplate
from anvil import *
import anvil.server

class Index(IndexTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    self.dropdown_1.items = anvil.server.call('get_supported_regions')
  
  def button_cal_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  def drop_down_1_change(self, **event_args):
    """This method is called when an item is selected"""
    pass
