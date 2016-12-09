from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from .forms import UploadFileForm
from learn.tools.FileTools import handle_upload_file
from learn.text_analyse.text_train import text_analyse

#上传文件处理
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_upload_file(request.FILES.get('file', None))
            ftemp = request.FILES.get('file', None)
            print('ftemp: ', ftemp)
            return HttpResponseRedirect('/success/')
    else:
        form = UploadFileForm()

    return render(request, 'upload.html', {'form': form})


#上传成功跳转处理
def uploadFileResult(request):
    result = u'成功'
    res = text_analyse()
    return render(request, 'success1.html',
                  {'result': result,
                   'exist': res[0],
                   'file_md5': res[1],
                   'court': res[2],
                   'case_type': res[3],
                   'reference': res[4],
                   'cause_all': res[5],
                   'keyword_all':res[6]})
# Create your views here.
