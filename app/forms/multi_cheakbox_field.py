# app/forms/multi_checkboxes_field.py
from wtforms import SelectMultipleField
from wtforms.widgets import ListWidget, CheckboxInput

class MultiCheckboxField(SelectMultipleField):
    """
    Renders a list of checkboxes of a <select multiple>.
    """
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()
    