# %%
import panel as pn
pn.extension()
text = pn.widgets.TextInput(value='Ready')

name = "Button Example"

def b(event):
    text.value = 'Clicked {0} times'.format(button.clicks)
button = pn.widgets.Button(name='Click me', button_type='primary')    
button.on_click(b)
pn.Row(button, text).servable()