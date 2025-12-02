from django import forms
from .models import Planting, WorkSchedule, Harvest


class PlantingForm(forms.ModelForm):
    class Meta:
        model = Planting
        fields = ['greenhouse', 'vegetable_type', 'planting_date', 'planned_harvest_date']
        widgets = {
            'planting_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'planned_harvest_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class WorkScheduleForm(forms.ModelForm):
    class Meta:
        model = WorkSchedule
        fields = ['planting', 'work_type', 'planned_date', 'actual_date', 'status']
        widgets = {
            'planned_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'actual_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class HarvestForm(forms.ModelForm):
    class Meta:
        model = Harvest
        fields = ['planting', 'harvest_date', 'quantity', 'unit', 'quality']
        widgets = {
            'harvest_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})