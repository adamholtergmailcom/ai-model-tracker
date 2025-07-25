# AI Model Tracker

A self-updating dashboard that tracks AI model releases from OpenRouter and fal.ai, automatically enriches data via the Perplexity API, and publishes updates to GitHub Pages.

## 🚀 Live Dashboard

**The dashboard is now live and publicly accessible at:**
**https://adamholtergmailcom.github.io/ai-model-tracker/**

You can embed this URL in an iframe on any website:
```html
<iframe src="https://adamholtergmailcom.github.io/ai-model-tracker/" 
        width="100%" 
        height="800" 
        frameborder="0">
</iframe>
```

## Features

- **Automated Discovery**: Monitors OpenRouter API and fal.ai for new model releases
- **Rich Metadata**: Uses Perplexity API to gather structured information about each model
- **Interactive Dashboard**: Modern web interface with charts and tables using Tailwind CSS and Chart.js
- **Self-Updating**: Daily cron job automatically updates data and publishes to GitHub Pages
- **Comprehensive Data**: Tracks 56+ models with performance benchmarks, pricing, and community commentary

## Project Structure

```
ai-model-tracker/
├── data/
│   └── models.json        # Central data file for all tracked models
├── public/
│   ├── index.html         # Client-side dashboard using TailwindCSS and Chart.js
│   └── script.js          # Fetches JSON data and renders tables/charts dynamically
├── server/
│   ├── app.py             # Simple Flask server to serve dashboard and expose JSON
│   ├── update_models.py   # Daily update script: checks for new models and updates JSON
│   └── requirements.txt   # Python dependencies
├── deploy.sh              # Automated deployment script
├── README.md              # This file
└── PROJECT_PLAN.md        # Detailed implementation plan
```

## Quick Start

### 1. Local Development

```bash
# Clone the repository
git clone https://github.com/adamholtergmailcom/ai-model-tracker.git
cd ai-model-tracker

# Set up Python environment
cd server
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set environment variables
export PERPLEXITY_API_KEY="your_perplexity_api_key_here"
export GITHUB_TOKEN="your_github_token_here"

# Run local server
python app.py
```

### 2. Automated Daily Updates

To set up daily automated updates:

1. **Set up environment variables** (add to your shell profile):
```bash
export PERPLEXITY_API_KEY="your_perplexity_api_key_here"
export GITHUB_TOKEN="your_github_token_here"
```

2. **Add to crontab** (runs daily at 9 AM):
```bash
# Edit crontab
crontab -e

# Add this line (adjust path as needed)
0 9 * * * /Users/adam/Downloads/ModelReporting/deploy.sh
```

3. **Test the update script**:
```bash
./deploy.sh
```

### 3. Manual Updates

You can also run updates manually:
```bash
# Update model data
python server/update_models.py

# Commit and push changes
git add data/models.json
git commit -m "Update model data"
git push origin main
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `PERPLEXITY_API_KEY` | API key for Perplexity AI | Yes |
| `GITHUB_TOKEN` | Personal Access Token for GitHub | Yes |

## Data Schema

Each model entry in `data/models.json` follows this structure:

```json
{
  "model_name": "Claude Opus 4",
  "provider": "Anthropic",
  "release_date": "2025-05-22",
  "modality": "language",
  "context_window": 200000,
  "parameters": null,
  "model_type": "hybrid reasoning",
  "performance": {
    "swe_bench_verified": 72.5,
    "livecodebench": null,
    "aime_2025": null,
    "math500": null,
    "mmlu": null,
    "intelligence_index": null,
    "humanity_last_exam": null,
    "gpqa": null
  },
  "price": {
    "input_per_million_tokens": 15.0,
    "output_per_million_tokens": 75.0
  },
  "notes": "World's best coding model with sustained multi-hour agentic performance",
  "community_comments": []
}
```

## Dashboard Features

### Timeline View
- Chronological display of model releases grouped by month
- Shows release dates and key highlights for each model

### Performance Charts
- Interactive bar chart of SWE-bench Verified scores
- Sortable and filterable data visualization
- Responsive design for mobile and desktop

### Model Table
- Comprehensive table with all model details
- Sortable columns and search functionality
- Truncated notes with full details on hover

## API Integration Details

### OpenRouter API
```python
# Fetches current model list
GET https://openrouter.ai/api/v1/models
```

### Perplexity API
```python
# Enriches model data with structured information
POST https://api.perplexity.ai/chat/completions
```

### Fal.ai Discovery
Currently uses web scraping since no public API is available. Monitors:
- Main models page
- Blog announcements
- API documentation updates

## Development

### Local Testing
```bash
# Start Flask server
python server/app.py

# Test update script
python server/update_models.py

# Check logs
tail -f update.log
```

### Adding New Data Sources
To add new model providers:
1. Create discovery function in `update_models.py`
2. Add to `discovered` set in `update_models()`
3. Update Perplexity prompt if needed
4. Test with sample data

## Troubleshooting

### Common Issues
- **Dashboard not loading**: Check that GitHub Pages is enabled and files are in correct directories
- **API errors**: Verify environment variables are set correctly
- **GitHub push fails**: Ensure PAT has proper permissions and repository exists
- **Cron job not running**: Check cron logs and file permissions

### Debug Mode
Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License
MIT License - see LICENSE file for details

## Acknowledgments
- Data sources: OpenRouter, fal.ai, Perplexity AI
- Community insights: Reddit, ArtificialAnalysis.ai, LMArena
- UI Framework: Tailwind CSS, Chart.js
- Hosting: GitHub Pages