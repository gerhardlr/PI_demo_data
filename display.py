import asyncio
from IPython.display import display
from tango.asyncio import DeviceProxy
from tango import CommunicationFailed, DevFailed
import ipywidgets as widgets

        
async def poll_background(widget,device="sys/tg_test/1",attribute_to_read='State',mapping=None,resolution=0.2):
    while True:
        dev = await DeviceProxy(device)
        try:
            result = await dev.read_attribute(attribute_to_read)
            if (mapping != None):
                result = mapping[result.value]
            else:
                result = result.value
        except DevFailed as df:
            result = 'Failed to read {0}: \n {1}'.format(attribute_to_read,df)
        widget.update_value(str(result))
        await asyncio.sleep(resolution)
 
 
class ennum_widget:
    
    def __init__(self,description,options):
        self.widget = widgets.RadioButtons(
        options=options,
        description=description,
        layout={'width': 'max-content'},
        style = {'description_width': 'initial'},
        disabled=True)
    
    def update_value(self,value):
        self.widget.value = value
    
    def get_actual_widget(self):
        return self.widget

class text_widget:
    
    def __init__(self,prefix):
        self.prefix = prefix
        self.widget = widgets.Label(
        value=prefix)
        
    def update_value(self,value):
        self.widget.value = self.prefix+value
    
    def get_actual_widget(self):
        return self.widget

class text_box():
    
    def __init__(self,spec):
        self.par = [
            {'widget':text_widget('{0} for {1}: '.format(spec['attr'],x)),
            'device' : x,
            'attr': spec['attr'],
            'mapping' :spec['mapping']} 
            for x in spec['names']]
        self.box = widgets.VBox([item['widget'].get_actual_widget() for item in self.par])
        self.tasks = []
        
    def display(self):
        display(self.box)
        
    def run(self,resolution = 0.2):
        for item in self.par:
            self.tasks.append(asyncio.create_task(poll_background(item['widget'],item['device'],item['attr'],item['mapping'],resolution)))
    
    def stop(self):
        for task in self.tasks:
            task.cancel()

class ennum_box():
    
    def __init__(self,spec):
        self.pars = []
        for x in spec['names']:
            par = {}
            description = '{0} \n {1}: '.format(spec['attr'],x)
            options = list(spec['mapping'].values())
            par['widget'] = ennum_widget(description,options)
            par['device'] = x
            par['attr'] = spec['attr']
            par['mapping'] = spec['mapping']
            self.pars.append(par)
        self.box = widgets.VBox([item['widget'].get_actual_widget() for item in self.pars])
        self.tasks = []
        
    def display(self):
        display(self.box) 
        
    def run(self,resolution = 0.2):
        for item in self.pars:
            self.tasks.append(asyncio.create_task(poll_background(item['widget'],item['device'],item['attr'],item['mapping'],resolution)))
    
    def stop(self):
        for task in self.tasks:
            task.cancel()
        