#!/usr/bin/env python3
"""
Test script to verify social sharing functionality works correctly.
"""
import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'byte_board_blog.settings')
django.setup()

from blog.models import Post, Category, Tag


def test_social_sharing():
    """Test social sharing functionality."""
    print("Testing social sharing functionality...")
    
    # Create test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )
    
    # Create test post
    post, created = Post.objects.get_or_create(
        title='Test Post for Social Sharing',
        defaults={
            'slug': 'test-post-social-sharing',
            'author': user,
            'content': 'This is a test post for social sharing functionality.',
            'status': 'published'
        }
    )
    
    client = Client()
    
    # Test 1: Check if post detail page loads correctly
    print(f"1. Testing post detail page access...")
    post_url = reverse('blog:post_detail', kwargs={'slug': post.slug})
    response = client.get(post_url)
    print(f"   Post detail URL: {post_url}")
    print(f"   Response status: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✓ Post detail page loads successfully")
    else:
        print("   ✗ Post detail page failed to load")
        return False
    
    # Test 2: Check get_absolute_url method
    print(f"2. Testing get_absolute_url method...")
    absolute_url = post.get_absolute_url()
    print(f"   get_absolute_url returns: {absolute_url}")
    
    if absolute_url == post_url:
        print("   ✓ get_absolute_url returns correct URL")
    else:
        print("   ✗ get_absolute_url returns incorrect URL")
        print(f"   Expected: {post_url}")
        print(f"   Got: {absolute_url}")
        return False
    
    # Test 3: Check if share_post URL is accessible
    print(f"3. Testing share_post URL accessibility...")
    share_url = reverse('blog:share_post', kwargs={'pk': post.pk})
    print(f"   Share URL: {share_url}")
    
    # Test POST request to share_post view (simulating button click)
    response = client.post(share_url, {'mastodon': 'true'})
    print(f"   Share POST response status: {response.status_code}")
    
    if response.status_code == 302:  # Should redirect back to post
        print("   ✓ Share functionality accessible (redirect as expected)")
        redirect_url = response.url
        print(f"   Redirects to: {redirect_url}")
        
        if redirect_url == absolute_url:
            print("   ✓ Redirects to correct post URL")
        else:
            print("   ✗ Redirects to incorrect URL")
            return False
    else:
        print("   ✗ Share functionality failed")
        return False
    
    # Test 4: Check if social sharing buttons appear on page
    print(f"4. Testing social sharing buttons in template...")
    if 'Share on Mastodon' in response.content.decode() or 'blog:share_post' in str(response.content):
        print("   ✓ Social sharing elements found in template")
    else:
        # Get the actual post detail page content
        detail_response = client.get(post_url)
        if 'Share on Mastodon' in detail_response.content.decode():
            print("   ✓ Social sharing buttons found in post detail page")
        else:
            print("   ✗ Social sharing buttons not found")
            return False
    
    print("\n✓ All social sharing tests passed successfully!")
    return True


if __name__ == '__main__':
    success = test_social_sharing()
    if success:
        print("Social sharing functionality is working correctly.")
        sys.exit(0)
    else:
        print("Social sharing functionality has issues.")
        sys.exit(1)