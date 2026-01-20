from django import forms
from django.contrib.admin.widgets import AdminDateWidget, AdminSplitDateTime
from django.utils.safestring import mark_safe


class JSONFieldWidget(forms.Textarea):
    def __init__(self, attrs=None):
        default_attrs = {'cols': 80, 'rows': 5}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)


class ArrayFieldWidget(forms.Textarea):
    def __init__(self, attrs=None):
        default_attrs = {'cols': 80, 'rows': 3}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)


class TagInputWidget(forms.TextInput):
    def __init__(self, attrs=None):
        default_attrs = {'placeholder': '输入标签，用逗号分隔'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)


class BudgetRangeWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        widgets = (
            forms.NumberInput(attrs={'placeholder': '最低预算'}),
            forms.NumberInput(attrs={'placeholder': '最高预算'}),
        )
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return [value.get('min'), value.get('max')]
        return [None, None]

    def value_from_datadict(self, data, files, name):
        return {
            'min': data.get(f'{name}_0'),
            'max': data.get(f'{name}_1')
        }


class GroupSizeWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        widgets = (
            forms.NumberInput(attrs={'placeholder': '成人', 'min': 0}),
            forms.NumberInput(attrs={'placeholder': '儿童', 'min': 0}),
            forms.NumberInput(attrs={'placeholder': '老人', 'min': 0}),
        )
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return [value.get('adults'), value.get('children'), value.get('seniors')]
        return [0, 0, 0]

    def value_from_datadict(self, data, files, name):
        return {
            'adults': data.get(f'{name}_0'),
            'children': data.get(f'{name}_1'),
            'seniors': data.get(f'{name}_2')
        }


class DateRangeWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        widgets = (
            AdminDateWidget(attrs={'placeholder': '开始日期'}),
            AdminDateWidget(attrs={'placeholder': '结束日期'}),
        )
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            if isinstance(value, dict):
                return [value.get('start'), value.get('end')]
        return [None, None]

    def value_from_datadict(self, data, files, name):
        return {
            'start': data.get(f'{name}_0'),
            'end': data.get(f'{name}_1')
        }


class DestinationCitiesWidget(forms.Textarea):
    def __init__(self, attrs=None):
        default_attrs = {
            'cols': 80,
            'rows': 3,
            'placeholder': '输入目的地城市，每行一个城市'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)


class MustVisitSpotsWidget(forms.Textarea):
    def __init__(self, attrs=None):
        default_attrs = {
            'cols': 80,
            'rows': 3,
            'placeholder': '输入必游景点，每行一个景点'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)


class AvoidActivitiesWidget(forms.Textarea):
    def __init__(self, attrs=None):
        default_attrs = {
            'cols': 80,
            'rows': 3,
            'placeholder': '输入避免的活动，每行一个活动'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)


class ReadOnlyWidget(forms.Widget):
    def __init__(self, attrs=None):
        super().__init__(attrs)

    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            return '-'
        return mark_safe(f'<span class="readonly">{value}</span>')

    def value_from_datadict(self, data, files, name):
        return None
