from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect
# Create your views here.
def login(request):
    # return HttpResponse("Hello, You have logged in!")
    return render(request, 'login.html')

def index(request):
    # return render(request, 'index.html')
    context = {
        'title': 'Welcome to My Website',
        'message': 'This is a dynamic message from the server!',
        'items': ['Item 1', 'Item 2', 'Item 3'],
    }
    # 渲染模板并传递数据
    return render(request, 'index.html', context)