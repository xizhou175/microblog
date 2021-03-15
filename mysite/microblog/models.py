from django.db import models
from datetime import datetime
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import AbstractUser
from hashlib import md5


# Create your models here.
class User(AbstractUser):
    username = models.CharField(max_length=64, db_index=True, unique=True)
    email = models.EmailField(unique=True, db_index=True)
    password = models.CharField(max_length=128)
    about_me = models.CharField(max_length=140, null=True)
    following = models.ManyToManyField(to='User')  # users followed by this user

    def __str__(self):
        return '<User {}>'.format(self.username)

    def avatar_128(self):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, 128)

    def avatar_36(self):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, 36)

    def is_following(self, user):
        return self.following.filter(username=user.username).count() > 0

    def follow(self, user):
        if not self.is_following(user):
            self.following.add(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.following.remove(user)

    def followed_posts(self):
        selfuser = User.objects.prefetch_related('following__post').get(username=self.username)
        all_posts = Post.objects.filter(user__username=selfuser.username).all()
        for u in selfuser.following.all():
            all_posts = all_posts | u.post.all()
        return all_posts.order_by('timestamp')


class Post(models.Model):
    body = models.CharField(max_length=140)
    timestamp = models.DateTimeField(db_index=True, default=datetime.utcnow)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post')

    def __repr__(self):
        return '<Post {}>'.format(self.body)
