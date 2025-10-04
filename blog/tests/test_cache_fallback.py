"""
Test cache fallback behavior when cache backend is unavailable.
Simulates cache failures and tests that the application continues to work gracefully.
"""

from unittest.mock import patch
from django.test import TestCase
from django.core.cache import cache
from django.contrib.auth.models import User

from blog.models import Post, Category, Tag
from blog.utils import get_cached_common_context


class CacheFallbackTestCase(TestCase):
    """
    Test cache fallback behavior with simulated failures.
    
    This test case verifies that the application continues to work
    gracefully when the cache backend is unavailable.
    """
    
    @classmethod
    def setUpTestData(cls):
        """Create test data for fallback testing."""
        # Create test user
        cls.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test category
        cls.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        
        # Create test tag
        cls.tag = Tag.objects.create(
            name='Test Tag',
            slug='test-tag'
        )
        
        # Create test post
        cls.post = Post.objects.create(
            title='Test Post for Fallback',
            slug='test-post-fallback',
            content='# Test Content\n\nThis is a test post for fallback testing.',
            author=cls.user,
            status='published'
        )
        cls.post.categories.add(cls.category)
        cls.post.tags.add(cls.tag)
    
    def setUp(self):
        """Clear cache before each test."""
        cache.clear()
    
    def tearDown(self):
        """Clear cache after each test."""
        cache.clear()
    
    def test_normal_cache_operations(self):
        """Test that normal cache operations work before testing failures."""
        cache.set("test_key", "test_value", 60)
        value = cache.get("test_key")
        self.assertEqual(value, "test_value",
                        "Normal cache operations should work")
    
    def test_cache_get_failure_handling(self):
        """Test that cache.get() failure is handled gracefully."""
        with patch('django.core.cache.cache.get') as mock_get:
            mock_get.side_effect = Exception("Cache backend unavailable")
            
            # This should not raise an exception due to fallback handling
            context = get_cached_common_context()
            
            # Verify all required context keys are present
            self.assertIn('categories', context,
                         "Context should contain categories despite cache failure")
            self.assertIn('tags', context,
                         "Context should contain tags despite cache failure")
            self.assertIn('archive_dates', context,
                         "Context should contain archive_dates despite cache failure")
    
    def test_cache_set_failure_handling(self):
        """Test that cache.set() failure is handled gracefully."""
        with patch('django.core.cache.cache.set') as mock_set:
            mock_set.side_effect = Exception("Cache backend unavailable")
            
            # This should not raise an exception due to fallback handling
            context = get_cached_common_context()
            
            # Verify all required context keys are present
            self.assertIn('categories', context,
                         "Context should contain categories despite cache failure")
            self.assertIn('tags', context,
                         "Context should contain tags despite cache failure")
            self.assertIn('archive_dates', context,
                         "Context should contain archive_dates despite cache failure")


class PostModelCacheFallbackTestCase(TestCase):
    """
    Test Post model caching methods with simulated failures.
    
    This test case verifies that Post model caching methods handle
    cache failures gracefully and fall back to database operations.
    """
    
    @classmethod
    def setUpTestData(cls):
        """Create test data for Post model fallback testing."""
        # Create test user
        cls.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test category
        cls.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        
        # Create test tag
        cls.tag = Tag.objects.create(
            name='Test Tag',
            slug='test-tag'
        )
        
        # Create test post
        cls.post = Post.objects.create(
            title='Test Post for Fallback',
            slug='test-post-fallback',
            content='# Test Content\n\nThis is a test post for fallback testing.',
            author=cls.user,
            status='published'
        )
        cls.post.categories.add(cls.category)
        cls.post.tags.add(cls.tag)
    
    def setUp(self):
        """Clear cache before each test."""
        cache.clear()
    
    def tearDown(self):
        """Clear cache after each test."""
        cache.clear()
    
    def test_get_cached_content_with_cache_get_failure(self):
        """Test Post.get_cached_content() handles cache.get() failure gracefully."""
        with patch('blog.models.cache.get') as mock_get:
            mock_get.side_effect = Exception("Cache backend unavailable")
            
            content = self.post.get_cached_content()
            
            # Verify content is generated despite cache failure
            self.assertIsNotNone(content,
                               "Content should be generated despite cache failure")
            self.assertIn('Test Content</h1>', content,
                         "Content should be properly rendered despite cache failure")
    
    def test_get_cached_content_with_cache_set_failure(self):
        """Test Post.get_cached_content() handles cache.set() failure gracefully."""
        with patch('blog.models.cache.set') as mock_set:
            mock_set.side_effect = Exception("Cache backend unavailable")
            
            content = self.post.get_cached_content()
            
            # Verify content is generated despite cache failure
            self.assertIsNotNone(content,
                               "Content should be generated despite cache failure")
            self.assertIn('Test Content</h1>', content,
                         "Content should be properly rendered despite cache failure")
    
    def test_summary_property_with_cache_get_failure(self):
        """Test Post.summary property handles cache.get() failure gracefully."""
        with patch('blog.models.cache.get') as mock_get:
            mock_get.side_effect = Exception("Cache backend unavailable")
            
            summary = self.post.summary
            
            # Verify summary is generated despite cache failure
            self.assertIsNotNone(summary,
                               "Summary should be generated despite cache failure")
            self.assertIn('This is a test post', summary,
                         "Summary should contain content despite cache failure")
    
    def test_summary_property_with_cache_set_failure(self):
        """Test Post.summary property handles cache.set() failure gracefully."""
        with patch('blog.models.cache.set') as mock_set:
            mock_set.side_effect = Exception("Cache backend unavailable")
            
            summary = self.post.summary
            
            # Verify summary is generated despite cache failure
            self.assertIsNotNone(summary,
                               "Summary should be generated despite cache failure")
            self.assertIn('This is a test post', summary,
                         "Summary should contain content despite cache failure")


class CompleteCacheBackendFailureTestCase(TestCase):
    """
    Test behavior when entire cache backend is unavailable.
    
    This test case simulates complete cache backend failure across
    all modules and verifies the application continues to work.
    """
    
    @classmethod
    def setUpTestData(cls):
        """Create test data for complete cache failure testing."""
        # Create test user
        cls.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test category
        cls.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        
        # Create test tag
        cls.tag = Tag.objects.create(
            name='Test Tag',
            slug='test-tag'
        )
        
        # Create test post
        cls.post = Post.objects.create(
            title='Test Post for Fallback',
            slug='test-post-fallback',
            content='# Test Content\n\nThis is a test post for fallback testing.',
            author=cls.user,
            status='published'
        )
        cls.post.categories.add(cls.category)
        cls.post.tags.add(cls.tag)
    
    def setUp(self):
        """Clear cache before each test."""
        cache.clear()
    
    def tearDown(self):
        """Clear cache after each test."""
        cache.clear()
    
    def test_complete_cache_backend_failure(self):
        """Test that application works when cache backend is completely unavailable."""
        # Mock both cache.get and cache.set to fail across all modules
        with patch('django.core.cache.cache.get') as mock_cache_get, \
             patch('django.core.cache.cache.set') as mock_cache_set:
            
            mock_cache_get.side_effect = Exception("Cache backend completely unavailable")
            mock_cache_set.side_effect = Exception("Cache backend completely unavailable")
            
            # Test get_cached_common_context works without cache
            context = get_cached_common_context()
            self.assertIn('categories', context,
                         "Context should work without cache backend")
            self.assertIn('tags', context,
                         "Context should work without cache backend")
            self.assertIn('archive_dates', context,
                         "Context should work without cache backend")
            
            # Test Post model methods work without cache
            post = Post.objects.get(title='Test Post for Fallback')
            
            content = post.get_cached_content()
            self.assertIsNotNone(content,
                               "Post content should work without cache backend")
            self.assertIn('Test Content</h1>', content,
                         "Post content should be rendered without cache backend")
            
            summary = post.summary
            self.assertIsNotNone(summary,
                               "Post summary should work without cache backend")
            self.assertIn('This is a test post', summary,
                         "Post summary should contain content without cache backend")
    
    def test_multiple_operations_without_cache(self):
        """Test multiple operations in sequence without cache backend."""
        with patch('django.core.cache.cache.get') as mock_cache_get, \
             patch('django.core.cache.cache.set') as mock_cache_set:
            
            mock_cache_get.side_effect = Exception("Cache unavailable")
            mock_cache_set.side_effect = Exception("Cache unavailable")
            
            # Perform multiple operations
            for _ in range(3):
                context = get_cached_common_context()
                self.assertIn('categories', context)
                
                post = Post.objects.get(title='Test Post for Fallback')
                content = post.get_cached_content()
                self.assertIsNotNone(content)
                
                summary = post.summary
                self.assertIsNotNone(summary)
