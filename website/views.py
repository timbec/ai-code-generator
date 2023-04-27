from django.shortcuts import render

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import SignUpForm

import openai
import os

from .models import Code

LANG_LIST = ['c', 'clike', 'cpp', 'csharp', 'css', 'dart', 'django', 'go', 'html', 'java', 'javascript', 'markup', 'markup-templating', 'matlab',
             'mongodb', 'objectivec', 'perl', 'php', 'powershell', 'python', 'r', 'regex', 'ruby', 'rust', 'sass', 'scala', 'sql', 'swift', 'yaml']

def get_openai_response(prompt, temperature, lang=None):
    openai.api_key = os.getenv('API_KEY')
    openai.Model.list()

    full_prompt = prompt
    if lang is not None:
        full_prompt = f"Respond only with code in {lang} language: {prompt}"

    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=full_prompt,
            temperature=temperature,
            max_tokens=1000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        return response['choices'][0]['text'].strip()
    except Exception as e:
        print(e)
        return None


def home(request):
    if request.method == "POST":
        code = request.POST['code']
        lang = request.POST['lang']
        if lang == "Select Programming Language":
            messages.success(request, "Please select a programming language")

        response = get_openai_response(code, 2, lang)

        if response is not None:
            record = Code(question=code, code_answer=response,
                          language=lang, user=request.user)
            record.save()

        return render(request, "home.html", {"lang_list": LANG_LIST, 'response': response, 'lang': lang})

    return render(request, "home.html", {"lang_list": LANG_LIST})


def suggest(request):
    if request.method == "POST":
        code = request.POST['code']
        lang = request.POST['lang']

        if lang == "Select Programming Language":
            messages.success(
                request, "Hey! You Forgot To Pick A Programming Language...")
            return render(request, 'suggest.html', {'lang_list': LANG_LIST, 'code': code, 'lang': lang, 'response': code})
        else:
            response = get_openai_response(code, 1)

            if response is not None:
                record = Code(question=code, code_answer=response,
                              language=lang, user=request.user)
                record.save()

            return render(request, 'suggest.html', {'lang_list': LANG_LIST, 'response': response, 'lang': lang})

    return render(request, 'suggest.html', {'lang_list': LANG_LIST})


def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You Have Been Logged In!  Woohoo!")
            return redirect('home')
        else:
            messages.success(request, "Error Logging In. Please Try Again...")
            return redirect('home')
    else:
        return render(request, 'home.html', {})


def logout_user(request):
    logout(request)
    messages.success(request, "You Have Been Logged Out... Have A Nice Day!")
    return redirect('home')


def register_user(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, "You Have Registered...Congrats!!")
            return redirect('home')

    else:
        form = SignUpForm()

    return render(request, 'register.html', {"form": form})


def past(request):
    if request.user.is_authenticated:
        code = Code.objects.filter(user_id=request.user.id)
        return render(request, 'past.html', {"code": code})
    else:
        messages.success(request, "You Must Be Logged In To View This Page")
        return redirect('home')


def delete_past(request, Past_id):
    past = Code.objects.get(pk=Past_id)
    past.delete()
    messages.success(request, "Deleted Successfully...")
    return redirect('past')
