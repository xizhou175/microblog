from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .forms import LoginForm, RegistrationForm, EditProfileForm, EmptyForm, PostForm
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import get_user, login as Login, logout as Logout
from django.contrib.auth.decorators import login_required
from .models import User, Post
from django.core.paginator import Paginator
import json


@login_required(login_url='/microblog/login/')
# Create your views here.
def index(request):
    current_user = get_user(request)

    form = PostForm(request.POST)
    if form.is_valid():
        formdata = form.cleaned_data
        post = Post(body=formdata['post'], user=current_user)
        post.save()
        messages.add_message(request, messages.INFO, 'Your post is now live')
        return HttpResponseRedirect(reverse('microblog:index'))

    '''
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    '''
    posts = current_user.followed_posts().all()
    paginator = Paginator(posts, 2)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'microblog/index.html', {'title': 'Home', 'current_user': current_user, 'posts': posts,
                                                    'form': form, 'page_obj': page_obj})


@login_required(login_url='/microblog/login/')
def user(request, username):
    current_user = get_user(request)
    user = User.objects.filter(username=username).first()
    following = current_user.is_following(user)

    posts = user.post.order_by('-timestamp')
    paginator = Paginator(posts, 2)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'microblog/user.html', {'user': user, 'posts': posts, 'current_user': current_user,
                                                   'following': following, 'page_obj': page_obj})


@login_required(login_url='/microblog/login')
def explore(request):
    current_user = get_user(request)
    posts = Post.objects.order_by('-timestamp').all()
    paginator = Paginator(posts, 2)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'microblog/index.html', {'title': 'Explore', 'posts': posts, 'current_user': current_user,
                                                    'page_obj': page_obj})


def login(request):
    if get_user(request).is_authenticated:
        return HttpResponseRedirect(reverse('microblog:index'))
    form = LoginForm(request.POST)
    if form.is_valid():
        formdata = form.cleaned_data
        user = User.objects.filter(username=formdata['username']).first()
        if user is None or not user.check_password(formdata['password']):
            messages.add_message(request, messages.INFO, 'Invalid username or password')
            return HttpResponseRedirect(reverse('microblog:login'))
        Login(request, user)
        next_page = request.GET.get('next')
        if not next_page:
            next_page = reverse('microblog:index')
        messages.add_message(request, messages.INFO, 'Login requested for user {}, remember_me={}'.format(
            formdata['username'], formdata['remember_me']))
        return HttpResponseRedirect(next_page)
    return render(request, 'microblog/login.html', {'form': form})


def logout(request):
    Logout(request)
    return HttpResponseRedirect(reverse('microblog:index'))


def register(request):
    if get_user(request).is_authenticated:
        return HttpResponseRedirect(reverse('microblog:index'))
    form = RegistrationForm(request.POST)
    if form.is_valid():
        formdata = form.cleaned_data
        user = User(username=formdata['username'], email=formdata['email'])
        user.set_password(formdata['password'])
        user.save()
        messages.add_message(request, messages.INFO, 'Congratulations, you are now a registered user!')
        return HttpResponseRedirect(reverse('microblog:login'))
    return render(request, 'microblog/register.html', {'title': 'Register', 'form': form})


@login_required(login_url='/microblog/login/')
def edit_profile(request):
    form = EditProfileForm(request.POST)

    current_user = get_user(request)
    if form.is_valid():
        formdata = form.cleaned_data
        current_user.username = formdata['username']
        current_user.about_me = formdata['about_me']
        current_user.save()
        return HttpResponseRedirect(reverse('microblog:user', args=(current_user.username,)))
    return render(request, 'microblog/edit_profile.html', {'form': form, 'current_user': current_user})


@login_required(login_url='/microblog/login/')
def follow(request, username):
    current_user = get_user(request)
    form = EmptyForm(request)
    if form.is_valid():
        user = User.objects.filter(username=username).first()
        if user is None:
            messages.add_message(request, messages.INFO, 'User {} not found.'.format(username))
            return HttpResponseRedirect(reverse('microblog:index'))
        if user == current_user:
            messages.add_message(request, messages.INFO, 'You cannot follow yourself'.format(username))
            return HttpResponseRedirect(reverse('microblog:user', args=(user.username,)))
        current_user.follow(user)
        messages.add_message(request, messages.INFO, 'You are following {}'.format(username))
        return HttpResponseRedirect(reverse('microblog:user', args=(user.username,)))
    else:
        print('invalid')
        return HttpResponseRedirect(reverse('microblog:index'))


@login_required(login_url='/microblog/login/')
def unfollow(request, username):
    current_user = get_user(request)
    form = EmptyForm(request)
    if form.is_valid():
        user = User.objects.filter(username=username).first()
        if user is None:
            messages.add_message(request, messages.INFO, 'User {} not found.'.format(username))
            return HttpResponseRedirect(reverse('microblog:index'))
        if user == current_user:
            messages.add_message(request, messages.INFO, 'You cannot unfollow yourself'.format(username))
            return HttpResponseRedirect(reverse('microblog:user', args=(user.username,)))
        current_user.unfollow(user)
        messages.add_message(request, messages.INFO, 'You are not following {}'.format(username))
        return HttpResponseRedirect(reverse('microblog:user', args=(user.username,)))
    else:
        print('invalid')
        return HttpResponseRedirect(reverse('microblog:index'))
