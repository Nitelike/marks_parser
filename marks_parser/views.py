from django.shortcuts import render, redirect
from django.http import HttpResponse
from django import forms
from . import schools_api

data = {}

def enter(request):
	form = EnterForm()

	if not request.GET.get('id') and not request.POST.get('login'):
		return render(request, 'marks_parser/enter.html', {'form': form})	

	if request.GET.get('id'):
		data['id'] = request.GET.get('id');
		marks = schools_api.parse(data['login'], data['password'], data['id'])
		data['marks'] = marks

		return render(request, 'marks_parser/enter.html', {'form': form, 'options': data['options'], 'marks': data['marks']})
	if request.POST.get('login'):
		data['login'] = request.POST.get('login')
		data['password'] = request.POST.get('password')
		options = schools_api.getChildren(data['login'], data['password'])
		data['options'] = options

		return render(request, 'marks_parser/enter.html', {'form': form, 'options': options})	
		

class EnterForm(forms.Form):
	login = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Логин'}), label='')
	password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Пароль'}), label='')

		