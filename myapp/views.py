from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from .models import Post, Category, Comment
from django.utils import timezone

def blog_index(request):
    posts = Post.objects.filter(status='published').order_by('-published_at')
    categories = Category.objects.all()
    
    paginator = Paginator(posts, 5)  # 每页显示5篇文章
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    
    return render(request, 'blog/index.html', {
        'posts': posts,
        'categories': categories,
    })

def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    comments = post.comments.filter(is_approved=True)
    
    if request.method == 'POST' and request.user.is_authenticated:
        content = request.POST.get('content')
        if content:
            Comment.objects.create(
                post=post,
                author=request.user,
                content=content
            )
            messages.success(request, '评论已提交，等待审核')
            return redirect('post_detail', post_id=post.id)
    
    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments,
    })

def category_posts(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    posts = Post.objects.filter(category=category, status='published').order_by('-published_at')
    
    paginator = Paginator(posts, 5)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    
    return render(request, 'blog/category_posts.html', {
        'category': category,
        'posts': posts,
    })

@login_required
def create_post(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category')
        status = request.POST.get('status', 'draft')  # 获取用户选择的状态
        
        if title and content and category_id:
            category = get_object_or_404(Category, id=category_id)
            post = Post.objects.create(
                title=title,
                content=content,
                author=request.user,
                category=category,
                status=status,
                published_at=timezone.now() if status == 'published' else None
            )
            messages.success(request, '文章已创建')
            return redirect('post_detail', post_id=post.id)
        else:
            messages.error(request, '请填写所有必填字段')
    
    categories = Category.objects.all()
    return render(request, 'blog/create_post.html', {
        'categories': categories,
    })

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        if password1 != password2:
            return render(request, 'blog/register.html', {'error_message': '两次输入的密码不一致'})
        
        if User.objects.filter(username=username).exists():
            return render(request, 'blog/register.html', {'error_message': '用户名已存在'})
        
        if User.objects.filter(email=email).exists():
            return render(request, 'blog/register.html', {'error_message': '邮箱已被注册'})
        
        user = User.objects.create_user(username=username, email=email, password=password1)
        login(request, user)
        messages.success(request, '注册成功！')
        return redirect('blog_index')
    
    return render(request, 'blog/register.html')

def user_posts(request, username):
    author = get_object_or_404(User, username=username)
    is_self = request.user == author
    status = request.GET.get('status', 'published')
    
    # 如果不是作者本人，只显示已发布的文章
    if not is_self:
        status = 'published'
    
    posts = Post.objects.filter(author=author, status=status).order_by('-published_at')
    
    paginator = Paginator(posts, 5)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    
    return render(request, 'blog/user_posts.html', {
        'author': author,
        'posts': posts,
        'is_self': is_self,
        'status': status,
    })

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    # 检查是否是文章作者
    if post.author != request.user:
        messages.error(request, '你没有权限编辑这篇文章')
        return redirect('post_detail', post_id=post_id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category')
        status = request.POST.get('status')
        
        if not all([title, content, category_id, status]):
            messages.error(request, '请填写所有必填字段')
            return redirect('edit_post', post_id=post_id)
        
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            messages.error(request, '所选分类不存在')
            return redirect('edit_post', post_id=post_id)
        
        # 更新文章
        post.title = title
        post.content = content
        post.category = category
        post.status = status
        
        # 如果文章从草稿改为发布，更新发布时间
        if status == 'published' and post.status == 'draft':
            post.published_at = timezone.now()
        
        post.save()
        messages.success(request, '文章更新成功')
        return redirect('post_detail', post_id=post_id)
    
    categories = Category.objects.all()
    return render(request, 'blog/edit_post.html', {
        'post': post,
        'categories': categories,
    })

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    # 检查是否是文章作者
    if post.author != request.user:
        messages.error(request, '你没有权限删除这篇文章')
        return redirect('post_detail', post_id=post_id)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, '文章已删除')
        return redirect('user_posts', username=request.user.username)
    
    return redirect('post_detail', post_id=post_id)

@login_required
def custom_logout(request):
    logout(request)
    messages.success(request, '您已成功退出登录')
    return redirect('blog_index')