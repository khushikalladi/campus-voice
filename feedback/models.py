from django.db import models
from django.contrib.auth.models import User


# ================= POST =================
class Post(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    CATEGORY_CHOICES = [
        ('academic','Academic'),
        ('teacher','Teacher'),
        ('hostel','Hostel'),
        ('canteen','Canteen'),
        ('placement','Placement'),
        ('general','General')
    ]

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    upvotes = models.ManyToManyField(User, related_name='upvoted_posts', blank=True)
    downvotes = models.ManyToManyField(User, related_name='downvoted_posts', blank=True)

    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        return self.content[:50]


# ================= COMMENT =================
class Comment(models.Model):

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.content[:30]}"


# ================= PROFILE =================
class StudentProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=50, unique=True)

    college = models.CharField(max_length=50)
    branch = models.CharField(max_length=50)

    anonymous_name = models.CharField(max_length=50)

    def __str__(self):
        return self.anonymous_name
    
# ================= REPORT ==================
class Report(models.Model):
    REPORT_CHOICES = [
        ('spam', 'Spam'),
        ('abuse', 'Abusive Content'),
        ('fake', 'Fake Information'),
        ('other', 'Other')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)

    reason = models.CharField(max_length=20, choices=REPORT_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'post', 'comment']

