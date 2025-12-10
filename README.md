# Lead Finder - Business Lead Discovery Platform

A production-ready Flask application that discovers and connects businesses using Google Places API. Find leads by location, business type, and website availability with real-time streaming results.

**Deployment**: Automated CI/CD via GitHub Actions to Hetzner Kubernetes | Last updated: 2025-01-08

## Overview

Lead Finder is a web-based tool that helps businesses and marketers discover potential leads by searching Google Places API. It provides real-time business discovery with filtering capabilities, map-based location selection, and CSV export functionality.

**Live URL**: https://leadfinder.janisrael.com

## Features

### Core Functionality

- **Location-Based Search** - Search businesses by geographic coordinates (latitude, longitude) with configurable radius up to 50km
- **Map-Based Location Picker** - Interactive Google Maps interface to visually select search locations
- **Business Type Filtering** - Filter results by multiple business types (restaurant, hotel, store, etc.) with preset suggestions
- **Website Availability Filter** - Filter businesses based on website presence (has website, no website, or both)
- **Real-Time Streaming Results** - Results appear in real-time as they are discovered, without page refresh
- **CSV Export** - Export discovered leads to CSV format for further analysis
- **Asynchronous Processing** - Background crawling ensures responsive user experience
- **SQLite Database** - Local storage of discovered businesses with timestamps

### Technical Features

- **RESTful API** - Clean API endpoints for programmatic access
- **Health Check Endpoint** - Kubernetes-ready health monitoring (`/api/health`)
- **Error Handling** - Comprehensive error handling for API failures and rate limits
- **Responsive Design** - Mobile-friendly interface with neumorphism UI design
- **Production Ready** - Docker containerization and Kubernetes deployment support

## Technology Stack

### Backend
- **Python 3.11** - Programming language
- **Flask 3.1.1** - Web framework
- **SQLite3** - Database for local storage
- **Gunicorn** - Production WSGI server
- **python-dotenv** - Environment variable management
- **requests** - HTTP client for Google Places API

### Frontend
- **HTML5/CSS3** - Modern web standards
- **JavaScript (ES6+)** - Client-side interactivity
- **Google Maps JavaScript API** - Map integration and location picker
- **Roboto Slab Font** - Typography

### Infrastructure
- **Docker** - Containerization
- **Kubernetes (k3s)** - Container orchestration
- **Nginx Ingress Controller** - HTTP/HTTPS routing
- **GitHub Actions** - CI/CD automation
- **Hetzner Cloud** - Cloud hosting

## Installation

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Google Places API key ([Get one here](https://console.cloud.google.com/))

### Local Development Setup

1. **Clone the repository:**
   ```bash
   git clone git@github.com:janisrael/lead-finder.git
   cd lead-finder
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Linux/Mac
   # or
   venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   # Create .env file
   cat > .env << EOF
   GOOGLE_PLACES_API_KEY=your-api-key-here
   PORT=6005
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   EOF
   ```

5. **Run the application:**
   ```bash
   python app.py
   ```

6. **Access the application:**
   Open your browser and navigate to:
   ```
   http://localhost:6005
   ```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GOOGLE_PLACES_API_KEY` | Google Places API key | None | Yes |
| `PORT` | Application port | `6005` (local), `5000` (Docker) | No |
| `DEBUG` | Flask debug mode | `False` | No |
| `SECRET_KEY` | Flask secret key | None | Yes (production) |
| `FLASK_ENV` | Flask environment | `production` | No |

### Google Places API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing project
3. Enable **Places API** and **Maps JavaScript API**
4. Create credentials (API Key)
5. Restrict the API key to **Places API** and **Maps JavaScript API** only
6. Add the key to your `.env` file or Kubernetes secrets

**Note**: Google Places API has usage limits and billing. Monitor your usage in Google Cloud Console.

## Usage

### Web Interface

1. **Set Location**
   - Enter coordinates manually (lat,lng format) or
   - Click "Pick from Map" to use the interactive map

2. **Configure Search Parameters**
   - Set radius (maximum 50km)
   - Select business types (type and press Enter, or choose from suggestions)
   - Choose website filter (Yes, No, or Both)

3. **Start Search**
   - Click "Search" button
   - Results will stream in real-time to the table below

4. **Export Results**
   - Click "Export as CSV" to download all discovered leads

### API Endpoints

#### `GET /api/health`
Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "ok",
  "service": "lead-finder",
  "version": "1.0"
}
```

#### `GET /crawl`
Start a new business discovery crawl.

**Parameters:**
- `location` (string, required) - Location coordinates in "lat,lng" format
- `radius` (number, required) - Search radius in kilometers (max 50)
- `types` (string, required) - Comma-separated business types
- `has_website` (string, optional) - Filter: "yes", "no", or "both" (default: "both")
- `keyword` (string, optional) - Additional keyword filter

**Example:**
```bash
curl "http://localhost:6005/crawl?location=50.0405,-110.6766&radius=20&types=restaurant,hotel&has_website=yes"
```

**Response:**
```json
{
  "status": "started"
}
```

#### `GET /stream`
Stream discovered businesses (polling endpoint).

**Parameters:**
- `last_id` (number, optional) - Last received business ID (default: 0)

**Example:**
```bash
curl "http://localhost:6005/stream?last_id=0"
```

**Response:**
```json
{
  "last_id": 150,
  "results": [
    {
      "id": 1,
      "name": "Restaurant Name",
      "address": "123 Main St",
      "phone": "+1-555-1234",
      "website": "https://example.com",
      "rating": 4.5,
      "types": ["restaurant", "food"],
      "status": "OPERATIONAL"
    }
  ]
}
```

## Project Structure

```
lead-finder/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker container definition
├── .dockerignore               # Docker build exclusions
├── .env.example                # Environment variables template
├── CI_CD_SECRETS.md            # CI/CD secrets documentation
├── README.md                   # This file
├── k8s/                        # Kubernetes manifests
│   ├── namespace.yaml          # Kubernetes namespace
│   ├── secret.yaml             # Kubernetes secrets template
│   ├── deployment.yaml         # Application deployment
│   ├── service.yaml            # Kubernetes service
│   └── ingress.yaml            # Nginx ingress configuration
├── .github/
│   └── workflows/
│       └── deploy.yml          # GitHub Actions CI/CD workflow
├── index.html                  # Main web interface
├── app.js                      # Frontend JavaScript
├── style.css                   # Stylesheet (neumorphism design)
├── templates/                  # Flask templates (if needed)
└── static/                     # Static assets
```

## Database Schema

### Table: `places`

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PRIMARY KEY | Auto-incrementing ID |
| `name` | TEXT | Business name |
| `address` | TEXT | Business address |
| `phone` | TEXT | Formatted phone number |
| `website` | TEXT | Business website URL |
| `rating` | REAL | Google rating (0.0-5.0) |
| `types` | TEXT | Comma-separated business types |
| `status` | TEXT | Business status (OPERATIONAL, etc.) |
| `fetched_at` | TIMESTAMP | Timestamp of discovery |

## Production Deployment

### Kubernetes Deployment

The application is deployed to Hetzner Kubernetes (k3s) using GitHub Actions CI/CD.

**Prerequisites:**
- Kubernetes cluster (k3s)
- Nginx Ingress Controller
- PersistentVolumeClaim for SQLite database

**Deployment Process:**
1. Push to `main` branch triggers CI/CD
2. Tests run automatically
3. Docker image is built on Hetzner server
4. Kubernetes manifests are applied
5. Application is available at `https://leadfinder.janisrael.com`

**Kubernetes Resources:**
- Namespace: `leadfinder`
- Deployment: `leadfinder-app` (2 replicas)
- Service: `leadfinder-service`
- Ingress: `leadfinder-ingress`
- PersistentVolumeClaim: `leadfinder-pvc` (1Gi for SQLite database)

### Docker Deployment

**Build image:**
```bash
docker build -t leadfinder:latest .
```

**Run container:**
```bash
docker run -d \
  -p 5000:5000 \
  -e GOOGLE_PLACES_API_KEY=your-api-key \
  -e SECRET_KEY=your-secret-key \
  -v leadfinder-data:/app/data \
  leadfinder:latest
```

## CI/CD Configuration

GitHub Actions automatically deploys to Hetzner Kubernetes on push to `main` branch.

**Required GitHub Secrets:**
- `HETZNER_SSH_PRIVATE_KEY` - SSH key for Hetzner server access
- `HETZNER_HOST` - Hetzner server IP address
- `GOOGLE_PLACES_API_KEY` - Google Places API key

See `CI_CD_SECRETS.md` for detailed setup instructions.

## API Rate Limits

Google Places API has the following limits:
- **Nearby Search**: 1,000 requests per day (free tier)
- **Place Details**: 150,000 requests per day (free tier)
- **Next Page Token**: Requires 2-second delay between requests

The application handles rate limits gracefully and displays appropriate error messages.

## Troubleshooting

### Common Issues

**Issue**: `Google Places API key not configured`  
**Solution**: Ensure `GOOGLE_PLACES_API_KEY` is set in environment variables or Kubernetes secrets.

**Issue**: `API Request Denied`  
**Solution**: Verify API key restrictions in Google Cloud Console. Ensure Places API and Maps JavaScript API are enabled.

**Issue**: `Database locked`  
**Solution**: SQLite may have locking issues with multiple workers. Consider using PostgreSQL for production with high concurrency.

**Issue**: `No results found`  
**Solution**: Verify location coordinates are correct. Check radius is not too small. Ensure business types are valid Google Places types.

**Issue**: `Connection timeout`  
**Solution**: Check network connectivity. Verify Google Places API is accessible from your server.

## Security Considerations

- **API Key Security**: Never commit API keys to version control. Use environment variables or Kubernetes secrets.
- **Input Validation**: All user inputs are validated before API calls.
- **Rate Limiting**: Consider implementing rate limiting for production use.
- **HTTPS**: Always use HTTPS in production (handled by Cloudflare and Nginx Ingress).
- **Database Security**: SQLite database files should have restricted permissions.

## Future Enhancements

- Email extraction from websites
- Lead scoring and prioritization
- Export to multiple formats (JSON, Excel)
- Saved search profiles
- Batch processing for multiple locations
- Integration with CRM systems
- Advanced filtering (rating, price level, etc.)
- Historical data tracking
- Analytics dashboard

## Contributing

Improvements welcome! Consider adding:
- Additional export formats
- Advanced filtering options
- User authentication
- Search history
- Favorite businesses
- Email notifications
- API documentation (OpenAPI/Swagger)

## License & Disclaimer

This tool uses Google Places API, which is subject to Google's Terms of Service. Users are responsible for:
- Complying with Google Places API Terms of Service
- Respecting rate limits and quotas
- Properly attributing Google data
- Ensuring they have permission to use business data

**Always:**
- Use API keys responsibly
- Monitor API usage and costs
- Respect business privacy
- Comply with applicable data protection regulations

---

## Credits

**Created By**: Jan Francis Israel  
**Website**: https://janisrael.com  
**HuggingFace**: https://huggingface.co/swordfish7412  
**GitHub**: https://github.com/janisrael/lead-finder

---

**Project**: Lead Finder  
**Version**: 1.0  
**Status**: Production Ready  
**Last Updated**: January 2025

---

**Note**: This application migrated from PHP to Python Flask for better maintainability and deployment flexibility. Legacy PHP files may still exist in the repository but are not actively used.
