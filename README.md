# Byte Board Blog

A modern blogging platform built with Django and ReactPy, designed for developers to share technical content with syntax highlighting and Markdown support.

## Project Overview

Byte Board Blog is a feature-rich blogging platform specifically designed for developers and technical writers. It supports Markdown formatting, syntax highlighting for code snippets, and offers a clean, responsive interface for both readers and content creators.

## Features

- Markdown content support
- Syntax highlighting for code blocks
- Responsive design
- Category and tag organization
- Search functionality
- SEO optimization
- Social sharing capabilities
- Third-party commenting system integration

## Installation

### Prerequisites

- Python 3.10+
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
   uv pip install -r requirements.txt
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

- `blog/`: Main application directory
  - `models.py`: Database models
  - `views.py`: View functions
  - `urls.py`: URL routing
  - `admin.py`: Admin interface configuration
- `byte_board_blog/`: Project settings directory
  - `settings.py`: Django settings
  - `urls.py`: Project-level URL routing
- `static/`: Static files (CSS, JS, images)
- `media/`: User-uploaded content
- `templates/`: HTML templates

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.