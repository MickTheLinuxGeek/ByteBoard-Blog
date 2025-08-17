# Byte Board Blog

A modern single-user blogging platform built with Django and ReactPy, designed for developers to share technical content with rich formatting and interactive components.

## Project Overview

Byte Board Blog is a feature-rich, component-based blogging platform specifically designed for developers and technical writers. Built with Django backend and ReactPy frontend components, it offers a modern, interactive blogging experience with Markdown support, syntax highlighting, and a responsive design.

## Features

### Core Features
- **Django + ReactPy Architecture**: Modern component-based frontend with Django backend
- **Markdown Content Support**: Full markdown rendering with preview capabilities
- **Syntax Highlighting**: Code blocks with Pygments syntax highlighting
- **Rich Text Editor**: EasyMDE integration for content creation
- **Responsive Design**: Mobile-first responsive layout with collapsible sidebar
- **Component-based UI**: Modular ReactPy components for maintainable code

### Content Management
- **Category and Tag Organization**: Hierarchical content organization
- **Post Status Management**: Draft, published, and scheduled posts
- **Search Functionality**: Full-text search across posts
- **Pagination**: Efficient content browsing
- **SEO Optimization**: Meta tags, sitemaps, and SEO-friendly URLs

### Advanced Features
- **REST API**: Full API access to content via Django REST Framework
- **Social Sharing**: Built-in social media sharing capabilities
- **Caching Support**: Performance optimization through caching mechanisms
- **Admin Interface**: Customized Django admin for content management
- **Time Zone Support**: Proper handling of publication dates and times

## Technology Stack

- **Backend**: Django 5.2.4+
- **Frontend**: ReactPy 1.1.0+ (Python-based React-like components)
- **Database**: SQLite (development) / PostgreSQL (production)
- **Async Support**: Django Channels with Daphne
- **Content Processing**: Markdown with Pygments syntax highlighting
- **API**: Django REST Framework
- **Package Management**: uv (modern Python package manager)

## Installation

### Prerequisites

- Python 3.13+
- uv (Python package manager)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/byte_board_blog.git
   cd byte_board_blog
   ```

2. Create and activate a virtual environment:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   uv sync
   ```

4. Apply migrations:
   ```bash
   python manage.py migrate
   ```

5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

7. Access the site at http://127.0.0.1:8000/

## Database Configuration

### Development Environment

By default, the project uses SQLite for development. This configuration is automatically applied when running the application locally.

SQLite configuration details:
- Database file: `db.sqlite3` in the project root
- Atomic requests: Enabled
- Connection timeout: 20 seconds

### Production Environment

For production, the application is configured to use PostgreSQL. To enable the production database:

1. Set the environment variable:
   ```bash
   export DJANGO_ENVIRONMENT=production
   ```

2. Configure the following environment variables for your PostgreSQL connection:
   ```bash
   export DB_NAME=your_database_name
   export DB_USER=your_database_user
   export DB_PASSWORD=your_database_password
   export DB_HOST=your_database_host
   export DB_PORT=your_database_port
   ```

3. If you're using a deployment platform like Heroku, configure these variables in your platform's settings.

## Project Structure

```
byte_board_blog/
├── blog/                           # Main blog application
│   ├── components/                 # ReactPy components
│   │   ├── post_detail.py         # Post detail view component
│   │   ├── post_list.py           # Post list component
│   │   ├── post_list_item.py      # Individual post item
│   │   ├── sidebar.py             # Navigation sidebar
│   │   ├── search_bar.py          # Search functionality
│   │   ├── pagination.py          # Pagination component
│   │   └── ...                    # Other UI components
│   ├── models.py                  # Database models (Post, Category, Tag)
│   ├── views.py                   # Django views
│   ├── api_views.py              # REST API endpoints
│   ├── serializers.py            # API serializers
│   ├── admin.py                  # Admin interface configuration
│   └── urls.py                   # URL routing
├── byte_board_blog/              # Project configuration
│   ├── settings.py               # Django settings
│   └── urls.py                   # Main URL configuration
├── templates/                    # Django templates
├── static/                       # Static files (CSS, JS, images)
├── media/                        # User-uploaded content
├── 01-design_docs/              # Project documentation
└── pyproject.toml               # Python dependencies (uv)
```

## Development Status

### Current Status (August 2025)
The project is **actively developed** with the following completed features:

✅ **Completed Features:**
- Core Django + ReactPy architecture
- Post management with rich text editing
- Category and tag organization
- Responsive design with mobile support
- SEO optimization with meta tags and sitemaps
- Search functionality
- REST API endpoints
- Admin interface customization
- Time zone handling fixes
- Social sharing preparation

🔧 **In Progress:**
- Social sharing links (Mastodon, BlueSky, GitHub/GitLab)
- Caching mechanism implementation
- Post content truncation improvements
- Image alt attribute validation

📋 **Planned Features:**
- Enhanced caching system
- Performance optimizations
- Comprehensive test coverage
- Documentation improvements

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.