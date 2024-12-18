from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from .models import Post, Category, Comment
from django.utils import timezone
from django.http import Http404
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
    # 修改查询逻辑，允许作者查看自己的草稿
    post = get_object_or_404(Post, id=post_id)
    
    # 如果文章是草稿且访问者不是作者，返回404
    if post.status == 'draft' and post.author != request.user:
        raise Http404("文章不存在")
    
    comments = post.comments.all().order_by('-created_at')
    
    if request.method == 'POST' and request.user.is_authenticated:
        content = request.POST.get('content')
        if content:
            comment = Comment.objects.create(
                post=post,
                author=request.user,
                content=content,
                is_approved=True
            )
            messages.success(request, '评论已发布')
            return redirect('post_detail', post_id=post.id)
    
    context = {
        'post': post,
        'comments': comments,
    }
    return render(request, 'blog/post_detail.html', context)

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
def create_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        
        if name:
            category = Category.objects.create(
                name=name,
                description=description
            )
            messages.success(request, '分类已创建')
            return redirect('create_post')
        else:
            messages.error(request, '请填写分类名称')
    
    return redirect('create_post')

@login_required
def create_post(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category')
        new_category = request.POST.get('new_category')
        new_category_desc = request.POST.get('new_category_description', '')
        status = request.POST.get('status', 'draft')
        
        # 处理新分类的创建
        if new_category:
            category = Category.objects.create(
                name=new_category,
                description=new_category_desc
            )
            category_id = category.id
        
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
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    
    # 先删除该分类下的所有文章
    Post.objects.filter(category=category).delete()
    
    # 然后删除分类
    category.delete()
    messages.success(request, '分类及其所有文章已删除')
    return redirect('blog_index')

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    # 检查是否是评论作者或文章作者
    if request.user != comment.author and request.user != comment.post.author:
        messages.error(request, '你没有权限删除这条评论')
        return redirect('post_detail', post_id=comment.post.id)
    
    if request.method == 'POST':
        post_id = comment.post.id
        comment.delete()
        messages.success(request, '评论已删除')
        return redirect('post_detail', post_id=post_id)
    
    return redirect('post_detail', post_id=comment.post.id)

@login_required
def custom_logout(request):
    logout(request)
    messages.success(request, '您已成功退出登录')
    return redirect('blog_index')

def profile_view(request):
    return render(request, 'accounts/profile.html')