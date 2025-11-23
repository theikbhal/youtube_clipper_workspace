from django import forms

class ApkBuildForm(forms.Form):
    app_name = forms.CharField(
        max_length=50,
        label="App Name",
        widget=forms.TextInput(attrs={"placeholder": "My Cool App"})
    )
    package_name = forms.CharField(
        max_length=100,
        label="Package Name (e.g. com.tawhid.myapp)",
        widget=forms.TextInput(attrs={"placeholder": "com.tawhid.myapp"})
    )
    html_content = forms.CharField(
        label="HTML Page Content",
        widget=forms.Textarea(attrs={"rows": 15, "placeholder": "<!DOCTYPE html>..."})
    )
    icon = forms.ImageField(
        required=False,
        label="App Icon (PNG, optional)"
    )
