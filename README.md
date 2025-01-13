# 🎓 Google Scholar Profile Scraper

A lightning-fast, robust Python tool for scraping publication data from Google Scholar profiles. Built on top of the [scholarly](https://scholarly.readthedocs.io/) library with smart rate limiting and error handling to reliably extract research metrics.

## ✨ Features

- 📚 **Complete Publication Data**: Extracts titles, citations, authors, venues, and abstracts
- 🛡️ **Anti-Block Protection**: Smart rate limiting and exponential backoff
- 📊 **Large Profile Support**: Handles profiles with hundreds of publications
- 💾 **Flexible Storage**: Saves to CSV with append support for incremental updates
- 📈 **Citation Analytics**: Shows top cited papers summary
- 🔄 **Resilient Operation**: Robust error handling with automatic retries

## 🚀 Installation

First, install UV if you haven't already:
```bash
# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Then install the scraper:
```bash
# Clone the repository
git clone https://github.com/yourusername/gscholar-scraper.git
cd gscholar-scraper

# Create and activate virtual environment
uv venv
source .venv/bin/activate  # On Unix
# or
.venv\Scripts\activate  # On Windows

# Install dependencies (10-100x faster than pip)
uv sync
```

## 🔧 Requirements

- Python >=3.11
- scholarly[tor] - Core Google Scholar scraping functionality
- pandas - Data handling and CSV export
- PySocks - Network proxy support

## 💻 Usage

```bash
# Basic usage with default settings
python scholar_scraper.py --profile_url "https://scholar.google.com/citations?user=YOUR_USER_ID"

# Limit number of papers to scrape
python scholar_scraper.py --profile_url "YOUR_URL" --limit 100

# Custom output file
python scholar_scraper.py --profile_url "YOUR_URL" --output "my_papers.csv"
```

## 📋 Output Format

The scraper generates a CSV file with the following columns:
- `researcher`: Profile owner's name
- `title`: Publication title
- `year`: Publication year
- `venue`: Publication venue (journal/conference)
- `citations`: Citation count
- `authors`: Full author list
- `first_author`: First author name
- `last_author`: Last author name
- `author_count`: Number of authors
- `abstract`: Paper abstract
- `url`: Link to publication

## 🛠️ Advanced Features

### Rate Limiting
- Implements exponential backoff between requests
- Random delays to avoid detection
- Configurable retry mechanism

### Error Handling
- Automatic retries on network failures
- Partial data recovery on incomplete scrapes
- Detailed error logging

## 📝 Example Output

```python
Top 5 most cited papers from this batch:
Title                                    Citations  Year  Venue              First Author
Deep Learning in Neural Networks         5000      2015  Neural Networks    J. Smith
Machine Learning Applications            3000      2017  Nature ML          A. Johnson
...
```

## ⚠️ Disclaimer

Please use responsibly and in accordance with Google Scholar's terms of service. Consider implementing appropriate delays between requests to avoid overloading their servers.

## 📄 License

MIT License - feel free to use for academic or commercial purposes.

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.
