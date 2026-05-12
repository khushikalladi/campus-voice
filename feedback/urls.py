from django.urls import path
from . import views

urlpatterns = [

    path('', views.home),
    path('create', views.create_post),

    path('post/<int:id>/', views.post_detail),
    path('upvote/<int:post_id>/', views.upvote_post, name='upvote'),

    path('login/',views.user_login),
    path('register/',views.register),
    path('logout/',views.user_logout),
    path('delete/<int:post_id>/', views.delete_post, name='delete_post'),
    path('downvote/<int:post_id>/', views.downvote_post, name='downvote'),
    path('delete-comment/<int:comment_id>/', views.delete_comment),
    path('report/post/<int:post_id>/', views.report_post),
    path('report/comment/<int:comment_id>/', views.report_comment),

    path('reports/', views.admin_reports, name='admin_reports'),
    path('reports/delete-comment/<int:comment_id>/', views.delete_comment_report),
    path('reports/delete-post/<int:post_id>/', views.delete_post_report),
]