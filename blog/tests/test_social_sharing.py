"""
Test social sharing functionality.

This test module verifies that social sharing features work correctly,
including post detail page access, URL generation, share functionality,
and template rendering of social sharing buttons.
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from blog.models import Post


class SocialSharingTestCase(TestCase):
    """Test social sharing functionality."""
    
    def setUp(self):
        """Set up test data before each test."""
        # Create test user
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        
        # Create test post
        self.post = Post.objects.create(
            title="Test Post for Social Sharing",
            slug="test-post-social-sharing",
            author=self.user,
            content="This is a test post for social sharing functionality.",
            status="published"
        )
        
        self.client = Client()
    
    def tearDown(self):
        """Clean up after each test."""
        pass
    
    def test_post_detail_page_access(self):
        """Test that post detail page loads correctly."""
        post_url = reverse('blog:post_detail', kwargs={'slug': self.post.slug})
        response = self.client.get(post_url)
        
        self.assertEqual(response.status_code, 200,
                        "Post detail page should load successfully")
    
    def test_get_absolute_url_method(self):
        """Test that get_absolute_url method returns correct URL."""
        post_url = reverse('blog:post_detail', kwargs={'slug': self.post.slug})
        absolute_url = self.post.get_absolute_url()
        
        self.assertEqual(absolute_url, post_url,
                        "get_absolute_url should return correct post detail URL")
    
    def test_share_post_url_accessibility(self):
        """Test that share_post URL is accessible and redirects correctly."""
        share_url = reverse('blog:share_post', kwargs={'pk': self.post.pk})
        post_url = self.post.get_absolute_url()
        
        # Test POST request to share_post view (simulating button click)
        response = self.client.post(share_url, {'mastodon': 'true'})
        
        # Should redirect back to post (302)
        self.assertEqual(response.status_code, 302,
                        "Share functionality should redirect (status 302)")
        
        # Verify redirect URL
        redirect_url = response.url
        self.assertEqual(redirect_url, post_url,
                        "Share should redirect to correct post URL")
    
    def test_social_sharing_buttons_in_template(self):
        """Test that social sharing buttons appear in post detail page."""
        post_url = reverse('blog:post_detail', kwargs={'slug': self.post.slug})
        response = self.client.get(post_url)
        
        content = response.content.decode()
        
        # Check for social sharing elements in template
        has_mastodon_button = 'Share on Mastodon' in content
        has_share_url = 'blog:share_post' in content or reverse('blog:share_post', kwargs={'pk': self.post.pk}) in content
        
        self.assertTrue(has_mastodon_button or has_share_url,
                       "Social sharing buttons should be present in post detail page")
