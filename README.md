# HackerNews Analyzer Backend

[Live API](https://flask-backend-gtbb.onrender.com)

This project is a Flask-based REST API that powers the HackerNews Analyzer frontend. It continuously scrapes Hacker News for trending stories, categorizes them by technology topics, and provides real-time data through optimized API endpoints. Built with Python Flask, PostgreSQL, and automated scraping with Beautiful Soup.

## Features

- **Automated Data Scraping:** Hourly GitHub Actions workflow scraping Hacker News for fresh content.
- **Smart Categorization:** Intelligent tagging system categorizing stories by technology topics (AI, Python, JavaScript, etc.).
- **RESTful API Design:** Clean, consistent endpoints with proper HTTP status codes and JSON responses.
- **Database Optimization:** PostgreSQL with efficient indexing and query optimization for fast data retrieval.
- **Pagination Support:** Backend pagination for efficient handling of large datasets with metadata.
- **CORS Configuration:** Properly configured for cross-origin requests from frontend applications.
- **Production Ready:** Gunicorn WSGI server with proper error handling and logging.
- **Real-time Trends:** Live calculation of trending topics based on story frequency and engagement.
- **Data Validation:** Comprehensive input validation and sanitization for all API endpoints.

## Getting Started

Set up the development environment with Python virtual environment and PostgreSQL database.

### To run locally

1. Clone the repository
   ```bash
   git clone https://github.com/v43rus/flask-backend.git
   cd flask-backend
   ```

2. Create virtual environment (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\\Scripts\\activate on Windows
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables
   ```bash
   # Create .env file with your database configuration
   DATABASE_URL=postgresql://username:password@localhost/hackernews_analyzer
   ```

5. Initialize database
   ```bash
   python -c "from app.db import init_db; init_db()"
   ```

6. Start development server
   ```bash
   python run.py
   ```

### To deploy to production

1. Configure production environment
   ```bash
   pip install gunicorn
   ```

2. Run with Gunicorn
   ```bash
   gunicorn --bind 0.0.0.0:$PORT wsgi:app
   ```

## Usage

### API Endpoints

- **GET `/api/scrape`** - Trigger manual scraping of Hacker News stories
- **GET `/api/trends`** - Retrieve trending topics with story counts by time period
- **GET `/api/tags`** - Get all available technology tags with story counts
- **GET `/api/posts`** - Fetch paginated posts with filtering by tag and time period
- **GET `/api/popular`** - Get most popular stories across all categories

### Query Parameters

- `tag` - Filter by technology category (e.g., 'python', 'ai', 'javascript')
- `period` - Time period filter ('today', 'week', 'month', 'year')
- `page` - Page number for pagination (default: 1)
- `limit` - Number of items per page (default: 12, max: 50)

## Technical Implementation

### Core Technologies
- **Flask:** Lightweight WSGI web application framework for Python
- **PostgreSQL:** Advanced open-source relational database with JSON support
- **Beautiful Soup:** Python library for parsing HTML and extracting data from web pages
- **Requests:** HTTP library for making API calls and web scraping
- **psycopg2:** PostgreSQL adapter for Python with high performance

### Key Features
- **Database Models:** Well-structured tables with proper relationships and constraints
- **Connection Pooling:** Efficient database connection management for high concurrency
- **Error Handling:** Comprehensive exception handling with proper HTTP status codes
- **Data Sanitization:** Input validation and SQL injection prevention
- **Logging System:** Structured logging for monitoring and debugging
- **Rate Limiting:** Prevents overwhelming of external APIs during scraping

### Performance Optimizations
- **Database Indexing:** Strategic indexes on frequently queried columns
- **Query Optimization:** Efficient SQL queries with proper joins and aggregations
- **Caching Strategy:** In-memory caching for frequently accessed data
- **Batch Processing:** Efficient bulk insert operations for scraped data
- **Async Processing:** Background tasks for time-intensive operations

## File Structure

```
flask-backend/
├── app/
│   ├── __init__.py          # Flask application factory
│   ├── main.py              # Main application routes
│   ├── db.py                # Database configuration and models
│   └── hn/                  # HackerNews module
│       ├── __init__.py
│       ├── routes.py        # API route handlers
│       ├── service.py       # Business logic and database operations
│       ├── popular.py       # Popular stories functionality
│       └── tags.py          # Tag categorization logic
├── .github/workflows/       # GitHub Actions automation
│   └── scrape.yml          # Hourly scraping workflow
├── requirements.txt         # Python dependencies
├── run.py                  # Development server entry point
├── wsgi.py                 # Production WSGI entry point
├── render.yaml             # Render.com deployment configuration
├── schema.sql              # Database schema definition
└── README.md               # Project documentation
```

## Database Schema

### Stories Table
```sql
CREATE TABLE stories (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    url TEXT,
    score INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    author VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tags TEXT[]
);
```

### Indexes for Performance
```sql
CREATE INDEX idx_stories_created_at ON stories(created_at);
CREATE INDEX idx_stories_tags ON stories USING GIN(tags);
CREATE INDEX idx_stories_score ON stories(score DESC);
```

## Environment Configuration

### Development
```bash
DATABASE_URL=postgresql://localhost/hackernews_dev
FLASK_ENV=development
FLASK_DEBUG=True
```

### Production
```bash
DATABASE_URL=postgresql://production_db_url
FLASK_ENV=production
PORT=5000
```

## Deployment

### Render.com (Current Production)
- **Platform:** Render.com with automatic deployments
- **Server:** Gunicorn WSGI with proper process management
- **Database:** PostgreSQL with automated backups
- **URL:** https://flask-backend-gtbb.onrender.com

### GitHub Actions Automation
- **Scraping:** Hourly automated data collection
- **Deployment:** Automatic deployment on push to main branch
- **Monitoring:** Health checks and error notifications

## API Response Format

### Success Response
```json
{
  "success": true,
  "data": [...],
  "pagination": {
    "current_page": 1,
    "total_pages": 10,
    "total_items": 120,
    "items_per_page": 12
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message",
  "code": 400
}
```

## Browser Compatibility

- **CORS Headers:** Configured for all modern browsers
- **JSON API:** Standard REST endpoints compatible with all HTTP clients
- **Content-Type:** Proper MIME types for optimal browser handling
- **Error Codes:** Standard HTTP status codes for consistent error handling

## Development Workflow

### Scripts
- `python run.py` - Start development server with debug mode
- `python -m pytest` - Run test suite (if implemented)
- `pip freeze > requirements.txt` - Update dependencies
- `python -c "from app.hn.service import scrape_stories; scrape_stories()"` - Manual scraping

### Database Management
- **Migrations:** Manual schema updates with version control
- **Backups:** Automated daily backups on Render.com
- **Monitoring:** Real-time performance metrics and query analysis

## Security Features

- **SQL Injection Prevention:** Parameterized queries and ORM usage
- **CORS Configuration:** Controlled cross-origin resource sharing
- **Input Validation:** Comprehensive data sanitization and validation
- **Rate Limiting:** Protection against API abuse and DoS attacks
- **Environment Variables:** Secure handling of sensitive configuration

---

Built with ❤️ using Python Flask, PostgreSQL, Beautiful Soup, and modern API design principles. Powers the HackerNews Analyzer ecosystem.
