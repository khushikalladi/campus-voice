from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Comment, Report
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import StudentProfile
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.contrib.admin.views.decorators import staff_member_required
from .models import Report
from django.db import IntegrityError
from django.db.models import Count
import random

@login_required(login_url='/login/')
def home(request):

    profile, created = StudentProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'student_id': 'UNKNOWN',
            'college': 'UNKNOWN',
            'branch': 'UNKNOWN',
            'anonymous_name': 'Anonymous User'
        }
    )

    user_profile = profile
    category = request.GET.get('category')

    posts = Post.objects.filter(
        user__studentprofile__college=user_profile.college,
        user__studentprofile__branch=user_profile.branch,
        is_hidden=False
    )

    if category:
        posts = posts.filter(category=category)

    # 🔥 ORDER FIRST
    posts = posts.order_by('-created_at')

    # 🔥 THEN ADD THIS (CORRECT PLACE)
    for post in posts:
        post.already_reported = Report.objects.filter(
            post=post,
            user=request.user
        ).exists()

    # TRENDING POSTS
    trending_posts = Post.objects.filter(
        user__studentprofile__college=user_profile.college,
        user__studentprofile__branch=user_profile.branch,
        is_hidden=False
    ).annotate(
        total_upvotes=Count('upvotes')
    ).order_by('-total_upvotes')[:5]

    return render(request,'feedback/home.html',{
        'posts':posts,
        'trending_posts':trending_posts,
        'selected_category': category
    })

@login_required(login_url='/login/')
def create_post(request):

    if request.method == "POST":

        category = request.POST['category']
        content = request.POST['content']

        Post.objects.create(
            user=request.user,
            category=category,
            content=content
        )

        return redirect('/')

    return render(request,'feedback/create_post.html')


@login_required(login_url='/login/')
def post_detail(request, id):

    post = get_object_or_404(Post, id=id)

    comments = Comment.objects.filter(post=post).order_by('-created_at')

    # 🔥 ADD THIS LOOP
    for comment in comments:
        comment.already_reported = Report.objects.filter(
            comment=comment,
            user=request.user
        ).exists()

    if request.method == "POST":

        text = request.POST.get('content')

        if text:  # ✅ prevent empty comments
            Comment.objects.create(
                post=post,
                user=request.user,
                content=text   # 🔥 FIXED
            )

        return redirect(f'/post/{id}/')

    return render(request, 'feedback/post_detail.html', {
        'post': post,
        'comments': comments
    })

@login_required(login_url='/login/')
def upvote_post(request, post_id):

    post = get_object_or_404(Post, id=post_id)

    if request.user in post.upvotes.all():
        post.upvotes.remove(request.user)   # remove upvote
    else:
        post.upvotes.add(request.user)
        post.downvotes.remove(request.user)  # remove downvote if exists

    return redirect('/')

@login_required(login_url='/login/')
def downvote_post(request, post_id):

    post = get_object_or_404(Post, id=post_id)

    if request.user in post.downvotes.all():
        post.downvotes.remove(request.user)   # remove downvote
    else:
        post.downvotes.add(request.user)
        post.upvotes.remove(request.user)     # remove upvote if exists

    return redirect('/')

def register(request):

    if request.method == "POST":

        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        student_id = request.POST['student_id']

        # Example: 4MR22CS001
        college = student_id[:3]   # 4MR
        branch = student_id[5:7]   # CS 

         # 🔥 ADD THIS HERE
        if StudentProfile.objects.filter(student_id=student_id).exists():
            messages.error(request, "Student ID already exists ❌")
            return redirect('/register/')
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        anonymous_names = [
            "Anonymous Fox","Anonymous Raven","Anonymous Owl",
            "Anonymous Panther","Anonymous Tiger","Anonymous Wolf",
            "Anonymous Falcon","Anonymous Shark","Anonymous Dragon","Anonymous Eagle"
        ]

        random_name = random.choice(anonymous_names)

        # UNIQUE PART
        unique_id = user.id

        final_name = f"{random_name} #U{unique_id}"

        StudentProfile.objects.create(
            user=user,
            student_id=student_id,
            college=college,
            branch=branch,
            anonymous_name=final_name
        )

        return redirect('/login')

    return render(request,'feedback/register.html')

def user_login(request):

    if request.user.is_authenticated:
        return redirect('/')

    if request.method == "POST":

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/')

        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'feedback/login.html')

def user_logout(request):

    logout(request)

    return redirect('/login')

@login_required(login_url='/login/')
def delete_post(request, post_id):

    post = get_object_or_404(Post, id=post_id)

    # check if logged-in user is the creator
    if post.user == request.user:
        post.delete()

    return redirect('/')

@login_required(login_url='/login/')
def delete_comment(request, comment_id):

    comment = get_object_or_404(Comment, id=comment_id)

    # 🔥 Only owner can delete
    if comment.user == request.user:
        post_id = comment.post.id
        comment.delete()
        return redirect(f'/post/{post_id}/')

    return redirect('/')

@login_required(login_url='/login/')
def report_post(request, post_id):

    post = get_object_or_404(Post, id=post_id)

    if request.method == "POST":
        reason = request.POST.get('reason')

        try:
            Report.objects.create(
                user=request.user,
                post=post,
                reason=reason
            )
        except IntegrityError:
            # already reported → do nothing
            pass

        # 🔥 COUNT REPORTS
        total_reports = Report.objects.filter(post=post).count()

        if total_reports >= 3:
            post.is_hidden = True
            post.save()

        return redirect('/')

    return render(request, 'feedback/report.html', {'post': post})

@login_required(login_url='/login/')
def report_comment(request, comment_id):

    comment = get_object_or_404(Comment, id=comment_id)

    if request.method == "POST":
        reason = request.POST.get('reason')

        try:
            Report.objects.create(
                user=request.user,
                comment=comment,
                reason=reason
            )
        except:
            pass

        # 🔥 COUNT REPORTS
        total_reports = Report.objects.filter(comment=comment).count()

        # 🔥 AUTO DELETE AFTER 3
        if total_reports >= 3:
            post_id = comment.post.id
            Report.objects.filter(comment=comment).delete()
            comment.delete()
            return redirect(f'/post/{post_id}/')

        return redirect(f'/post/{comment.post.id}/')

    return render(request, 'feedback/report.html', {'comment': comment})

@staff_member_required
def admin_reports(request):

    reports = Report.objects.select_related('post', 'comment').order_by('-created_at')

    for report in reports:
        if report.post:
            report.total_reports = Report.objects.filter(post=report.post).count()
        elif report.comment:
            report.total_reports = Report.objects.filter(comment=report.comment).count()

    return render(request, 'feedback/admin_reports.html', {
        'reports': reports
    })

@login_required(login_url='/login/')
def delete_post_report(request, post_id):

    post = get_object_or_404(Post, id=post_id)

    if request.user.is_staff:
        post.delete()

    return redirect('/reports/')

@login_required(login_url='/login/')
def delete_comment_report(request, comment_id):

    comment = get_object_or_404(Comment, id=comment_id)

    if request.user.is_staff:
        # 🔥 DELETE ALL REPORTS FIRST
        Report.objects.filter(comment=comment).delete()

        # 🔥 THEN DELETE COMMENT
        comment.delete()

    return redirect('/reports/')

anonymous_names = [
"Anonymous Fox",
"Anonymous Raven",
"Anonymous Owl",
"Anonymous Panther",
"Anonymous Tiger",
"Anonymous Wolf",
"Anonymous Bat",
"Anonymous Shark",
"Anonymous Lion",
"Anonymous Falcon",
"Anonymous Dragon",
"Anonymous Eagle"
]