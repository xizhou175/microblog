from datetime import datetime, timedelta

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import User, Post


class UserModelTests(TestCase):

    def test_follow(self):
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        u1.save()
        u2.save()
        self.assertQuerysetEqual(u1.following.all(), [])
        self.assertQuerysetEqual(u1.user_set.all(), [])

        u1.follow(u2)
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.following.count(), 1)
        self.assertEqual(u1.following.first().username, 'susan')
        self.assertEqual(u2.user_set.count(), 1)
        self.assertEqual(u2.user_set.first().username, 'john')

        u1.unfollow(u2)
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.following.count(), 0)
        self.assertEqual(u2.user_set.count(), 0)

    def test_followed_posts(self):
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        u3 = User(username='mary', email='mary@example.com')
        u4 = User(username='david', email='david@example.com')
        u1.save()
        u2.save()
        u3.save()
        u4.save()

        now = datetime.utcnow()
        p1 = Post(body="post from john", user=u1,
                  timestamp=now + timedelta(seconds=1))
        p2 = Post(body="post from susan", user=u2,
                  timestamp=now + timedelta(seconds=4))
        p3 = Post(body="post from mary", user=u3,
                  timestamp=now + timedelta(seconds=3))
        p4 = Post(body="post from david", user=u4,
                  timestamp=now + timedelta(seconds=2))
        p1.save()
        p2.save()
        p3.save()
        p4.save()

        u1.follow(u2)  # john follows susan
        u1.follow(u4)  # john follows david
        u2.follow(u3)  # susan follows mary
        u3.follow(u4)  # mary follows david

        f1 = u1.followed_posts().all()
        f2 = u2.followed_posts().all()
        f3 = u3.followed_posts().all()
        f4 = u4.followed_posts().all()
        l1 = []
        l2 = []
        l3 = []
        l4 = []
        for q in f1:
            l1.append(q.id)
        for q in f2:
            l2.append(q.id)
        for q in f3:
            l3.append(q.id)
        for q in f4:
            l4.append(q.id)
        self.assertEqual(l1, [p1.pk, p4.pk, p2.pk])
        self.assertEqual(l2, [p3.pk, p2.pk])
        self.assertEqual(l3, [p4.pk, p3.pk])
        self.assertEqual(l4, [p4.pk])
