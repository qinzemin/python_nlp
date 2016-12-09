from django import forms


class UploadFileForm(forms.Form):
    #title = forms.CharField(max_length=50)
    title = "请选择上传文件"
    file = forms.FileField()
