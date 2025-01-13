import argparse
import pandas as pd
from typing import List, Dict
from scholarly import scholarly
from urllib.parse import urlparse, parse_qs
import time
import random
import os

# Your Google Scholar profile
DEFAULT_SCHOLAR_URL = "https://scholar.google.com/citations?user=zFqBbIkAAAAJ&hl=en"
DEFAULT_PAPER_LIMIT = 1000

class GoogleScholarScraper:
    def __init__(self):
        self.setup_conservative_settings()
        
    def setup_conservative_settings(self):
        """Set up conservative settings to avoid being blocked."""
        scholarly.set_timeout(30)  # Longer timeout
        scholarly.set_retries(10)  # More retries
        
    def extract_user_id(self, profile_url: str) -> str:
        """Extract user ID from Google Scholar URL."""
        parsed = urlparse(profile_url)
        params = parse_qs(parsed.query)
        return params.get('user', [None])[0]
    
    def parse_authors(self, author_str: str) -> List[str]:
        """Parse author string into list of individual authors."""
        if not author_str:
            return []
        # Split by 'and' and clean up each author name
        authors = [author.strip() for author in author_str.split(" and ")]
        return authors
        
    def scrape_scholar_page(self, profile_url: str, paper_limit: int = DEFAULT_PAPER_LIMIT) -> List[Dict]:
        """Scrape publications from a Google Scholar profile."""
        user_id = self.extract_user_id(profile_url)
        if not user_id:
            raise ValueError("Could not extract user ID from URL")
            
        try:
            # Search for author by ID - returns dict directly
            author = scholarly.search_author_id(user_id)
            if not author:
                raise Exception("Author not found")
            
            # Fill in complete author information
            author = scholarly.fill(author)
            
        except Exception as e:
            raise Exception(f"Failed to fetch author profile: {str(e)}")
        
        papers = []
        print(f"\nFound researcher: {author.get('name', 'Unknown')}")
        total_papers = min(len(author.get('publications', [])), paper_limit)
        print(f"\nScraping {total_papers} papers (out of {len(author.get('publications', []))})...\n")
        
        # Iterate through publications with exponential backoff
        for i, pub in enumerate(author.get('publications', []), 1):
            if i > paper_limit:
                break
                
            max_retries = 3
            for retry in range(max_retries):
                try:
                    # Random delay between requests with exponential backoff
                    delay = (2 ** retry) * random.uniform(1, 3)
                    time.sleep(delay)
                    
                    pub_filled = scholarly.fill(pub)
                    
                    # Extract venue information
                    bib = pub_filled.get('bib', {})
                    venue = bib.get('venue', '')
                    if not venue:
                        venue = bib.get('journal', '')
                    if not venue:
                        venue = bib.get('conference', '')
                    
                    # Extract and parse author information
                    author_str = bib.get('author', '')
                    if isinstance(author_str, list):
                        authors = author_str
                    else:
                        authors = self.parse_authors(author_str)
                    
                    first_author = authors[0] if authors else ''
                    last_author = authors[-1] if authors else ''
                    all_authors = ', '.join(authors)
                    
                    paper_data = {
                        'researcher': author.get('name', ''),
                        'title': bib.get('title', ''),
                        'year': bib.get('pub_year', ''),
                        'venue': venue,
                        'citations': pub_filled.get('num_citations', 0),
                        'abstract': bib.get('abstract', ''),
                        'url': pub_filled.get('pub_url', ''),
                        'authors': all_authors,
                        'first_author': first_author,
                        'last_author': last_author,
                        'author_count': len(authors)
                    }
                    papers.append(paper_data)
                    print(f"Scraped [{i}/{total_papers}]: {paper_data['title'][:100]}...")
                    break
                    
                except Exception as e:
                    if retry < max_retries - 1:
                        print(f"Retry {retry + 1}/{max_retries} for paper {i} due to: {str(e)}")
                        time.sleep((2 ** retry) * random.uniform(0, 1))  # Longer delay between retries
                    else:
                        print(f"Warning: Could not fetch details for paper {i} after {max_retries} retries: {str(e)}")
                        # Add partial data if available
                        try:
                            paper_data = {
                                'researcher': author.get('name', ''),
                                'title': pub.get('bib', {}).get('title', 'Unknown Title'),
                                'year': pub.get('bib', {}).get('pub_year', ''),
                                'venue': '',
                                'citations': pub.get('num_citations', 0),
                                'abstract': '',
                                'url': '',
                                'authors': '',
                                'first_author': '',
                                'last_author': '',
                                'author_count': 0
                            }
                            papers.append(paper_data)
                            print(f"Added partial data for paper {i}")
                        except:
                            print(f"Could not add partial data for paper {i}")
                
            # Random delay between papers
            time.sleep(random.uniform(0, 1))
                
        return papers

    def save_to_csv(self, papers: List[Dict], output_file: str):
        """Save scraped papers to CSV file."""
        if not papers:
            print("No papers were scraped. Please check if the profile URL is correct.")
            return
            
        df = pd.DataFrame(papers)
        
        # Reorder columns
        columns = [
            'researcher', 'title', 'year', 'venue', 'citations', 
            'authors', 'first_author', 'last_author', 'author_count',
            'abstract', 'url'
        ]
        df = df[columns]
        
        # Check if file exists to determine mode and header
        file_exists = os.path.isfile(output_file)
        df.to_csv(output_file, mode='a', header=not file_exists, index=False)
        print(f"\nAppended {len(papers)} papers to {output_file}")
        
        if len(papers) > 0:
            print("\nTop 5 most cited papers from this batch:")
            top_papers = df.nlargest(5, 'citations')[['title', 'citations', 'year', 'venue', 'first_author']]
            pd.set_option('display.max_colwidth', None)
            print(top_papers.to_string(index=False))

def main():
    parser = argparse.ArgumentParser(description='Scrape Google Scholar profile')
    parser.add_argument('--profile_url', type=str, default=DEFAULT_SCHOLAR_URL,
                      help=f'Google Scholar profile URL (default: {DEFAULT_SCHOLAR_URL})')
    parser.add_argument('--output', type=str, default='scholar_papers.csv',
                      help='Output CSV file path (default: scholar_papers.csv)')
    parser.add_argument('--limit', type=int, default=DEFAULT_PAPER_LIMIT,
                      help=f'Maximum number of papers to scrape (default: {DEFAULT_PAPER_LIMIT})')
    args = parser.parse_args()
    
    try:
        scraper = GoogleScholarScraper()
        print(f"Starting to scrape Google Scholar profile: {args.profile_url}")
        papers = scraper.scrape_scholar_page(args.profile_url, args.limit)
        scraper.save_to_csv(papers, args.output)
    except Exception as e:
        print(f"Error: {str(e)}")
        raise

if __name__ == "__main__":
    main() 