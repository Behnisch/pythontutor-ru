from json import dumps

from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render

from tutorial.models import Course, Lesson
from tutorial.views import DEFAULT_COURSE

from evaldontevil import execute_python_explain


def visualizer(request):
    if 'lesson' in request.GET:
        lesson = Lesson.objects.get(urlname=request.GET['lesson'])
        if lesson is not None:
            navigation = {'lesson': lesson}

    code = request.POST.get('code', '')
    input_data = request.POST.get('input', '')

    return render(request, 'visualizer.html', locals())


def execute(request):
    # AJAX request
    # method: POST
    # params: user_script, input_data
    post = request.POST
    if 'user_script' in post and 'input_data' in post:
        user_script = post['user_script']
        input_data = post['input_data']

        res = execute_python_explain(user_script, stdin=input_data)
        res = res.__dict__

        del res['stdout']
        del res['stderr']

        json_data = dumps(res)

        return HttpResponse(json_data, content_type='application/json')

    else:
        return HttpResponseBadRequest()
