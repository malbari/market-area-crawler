
#!/usr/bin/env python3
"""
Market Area Crawler - Sentiment Analysis Tool
Analizza siti web per sentiment su mercati specifici in diverse località
"""

import asyncio
import aiohttp
import json
import re
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import logging
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from textblob import TextBlob
import requests

# Configurazione logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class NewsArticle:
    """Rappresenta un articolo di news"""
    title: str
    content: str
    url: str
    date: Optional[datetime] = None
    market_areas: List[str] = None
    locations: List[str] = None
    sentiment_score: float = 0.0
    
class MarketAreaCrawler:
    """Crawler principale per l'analisi del sentiment di mercato"""
    
    def __init__(self, market_areas: List[str], locations: List[str]):
        self.market_areas = [area.lower() for area in market_areas]
        self.locations = [loc.lower() for loc in locations]
        self.session = None
        
        # Keyword per mercati (espandibili)
        self.market_keywords = {
            'tecnologia': ['tech', 'tecnologia', 'software', 'ai', 'intelligenza artificiale', 'startup'],
            'finanza': ['finanza', 'banking', 'banche', 'investimenti', 'mercati finanziari'],
            'energia': ['energia', 'petrolio', 'gas', 'rinnovabili', 'solare', 'eolico'],
            'automotive': ['auto', 'automotive', 'veicoli', 'trasporti', 'mobilità'],
            'immobiliare': ['immobiliare', 'real estate', 'case', 'proprietà', 'edilizia']
        }
        
        # Keyword per località
        self.location_keywords = {
            'italia': ['italia', 'italy', 'romano', 'milano', 'napoli', 'torino'],
            'europa': ['europa', 'europe', 'ue', 'european union', 'bruxelles'],
            'usa': ['usa', 'america', 'stati uniti', 'washington', 'new york'],
            'cina': ['cina', 'china', 'beijing', 'shanghai', 'hong kong'],
            'giappone': ['giappone', 'japan', 'tokyo', 'osaka'],
            'germania': ['germania', 'germany', 'berlino', 'monaco']
        }
    
    async def __aenter__(self):
        """Context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.session:
            await self.session.close()
    
    def extract_text_from_html(self, html: str) -> str:
        """Estrae testo pulito dall'HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Rimuovi script e style
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Estrai testo
        text = soup.get_text()
        
        # Pulisci il testo
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def analyze_sentiment(self, text: str) -> float:
        """Analizza il sentiment del testo usando TextBlob"""
        try:
            blob = TextBlob(text)
            # Normalizza il sentiment da [-1, 1] a [0, 100]
            sentiment = (blob.sentiment.polarity + 1) * 50
            return round(sentiment, 2)
        except Exception as e:
            logger.error(f"Errore nell'analisi sentiment: {e}")
            return 50.0  # Neutrale
    
    def find_market_areas(self, text: str) -> List[str]:
        """Trova i mercati menzionati nel testo"""
        found_markets = []
        text_lower = text.lower()
        
        for market, keywords in self.market_keywords.items():
            if market in self.market_areas:
                for keyword in keywords:
                    if keyword in text_lower:
                        found_markets.append(market)
                        break
        
        return found_markets
    
    def find_locations(self, text: str) -> List[str]:
        """Trova le località menzionate nel testo"""
        found_locations = []
        text_lower = text.lower()
        
        for location, keywords in self.location_keywords.items():
            if location in self.locations:
                for keyword in keywords:
                    if keyword in text_lower:
                        found_locations.append(location)
                        break
        
        return found_locations
    
    async def fetch_page(self, url: str) -> Optional[str]:
        """Scarica una pagina web"""
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    # Prova prima con encoding automatico
                    try:
                        return await response.text()
                    except UnicodeDecodeError:
                        # Se fallisce, usa encoding latin-1 come fallback
                        logger.warning(f"Problemi encoding per {url}, uso latin-1")
                        content = await response.read()
                        return content.decode('latin-1', errors='ignore')
                else:
                    logger.warning(f"Status {response.status} per {url}")
                    return None
        except Exception as e:
            logger.error(f"Errore nel fetch di {url}: {e}")
            return None
    
    def extract_articles_from_page(self, html: str, base_url: str) -> List[Dict]:
        """Estrae gli articoli da una pagina"""
        soup = BeautifulSoup(html, 'html.parser')
        articles = []
        
        # Cerca articoli comuni (da personalizzare per siti specifici)
        article_selectors = [
            'article',
            '.article',
            '.news-item',
            '.post',
            'h2 a',
            'h3 a',
            '.title a'
        ]
        
        for selector in article_selectors:
            elements = soup.select(selector)
            for element in elements:
                try:
                    if element.name == 'a':
                        title = element.get_text().strip()
                        link = element.get('href')
                    else:
                        title_elem = element.find(['h1', 'h2', 'h3', 'a'])
                        if title_elem:
                            title = title_elem.get_text().strip()
                            link = title_elem.get('href') if title_elem.name == 'a' else None
                        else:
                            continue
                    
                    if title and link:
                        full_url = urljoin(base_url, link)
                        articles.append({
                            'title': title,
                            'url': full_url,
                            'content': element.get_text().strip()[:500]  # Preview
                        })
                except Exception as e:
                    logger.debug(f"Errore nell'estrazione articolo: {e}")
                    continue
        
        return articles[:20]  # Limita a 20 articoli per pagina
    
    async def analyze_website(self, url: str) -> List[NewsArticle]:
        """Analizza un intero sito web"""
        logger.info(f"Analizzando sito: {url}")
        
        html = await self.fetch_page(url)
        if not html:
            return []
        
        articles_data = self.extract_articles_from_page(html, url)
        analyzed_articles = []
        
        for article_data in articles_data:
            try:
                # Scarica il contenuto completo dell'articolo
                article_html = await self.fetch_page(article_data['url'])
                if article_html:
                    content = self.extract_text_from_html(article_html)
                else:
                    content = article_data['content']
                
                # Analizza mercati e località
                found_markets = self.find_market_areas(content)
                found_locations = self.find_locations(content)
                
                # Processa solo se ci sono mercati e località rilevanti
                if found_markets and found_locations:
                    sentiment_score = self.analyze_sentiment(content)
                    
                    article = NewsArticle(
                        title=article_data['title'],
                        content=content[:1000],  # Primi 1000 caratteri
                        url=article_data['url'],
                        market_areas=found_markets,
                        locations=found_locations,
                        sentiment_score=sentiment_score,
                        date=datetime.now()
                    )
                    
                    analyzed_articles.append(article)
                    logger.info(f"Articolo rilevante: {article.title[:50]}...")
                
            except Exception as e:
                logger.error(f"Errore nell'analisi articolo {article_data.get('url', 'unknown')}: {e}")
                continue
        
        return analyzed_articles
    
    def generate_market_report(self, articles: List[NewsArticle]) -> Dict:
        """Genera un report aggregato per mercato e località"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_articles': len(articles),
            'markets': {},
            'locations': {},
            'market_location_matrix': {}
        }
        
        # Analisi per mercato
        for market in self.market_areas:
            market_articles = [a for a in articles if market in a.market_areas]
            if market_articles:
                avg_sentiment = sum(a.sentiment_score for a in market_articles) / len(market_articles)
                report['markets'][market] = {
                    'article_count': len(market_articles),
                    'average_sentiment': round(avg_sentiment, 2),
                    'sentiment_trend': 'positive' if avg_sentiment > 60 else 'negative' if avg_sentiment < 40 else 'neutral'
                }
        
        # Analisi per località
        for location in self.locations:
            location_articles = [a for a in articles if location in a.locations]
            if location_articles:
                avg_sentiment = sum(a.sentiment_score for a in location_articles) / len(location_articles)
                report['locations'][location] = {
                    'article_count': len(location_articles),
                    'average_sentiment': round(avg_sentiment, 2),
                    'sentiment_trend': 'positive' if avg_sentiment > 60 else 'negative' if avg_sentiment < 40 else 'neutral'
                }
        
        # Matrice mercato-località
        for market in self.market_areas:
            for location in self.locations:
                key = f"{market}_{location}"
                relevant_articles = [
                    a for a in articles 
                    if market in a.market_areas and location in a.locations
                ]
                if relevant_articles:
                    avg_sentiment = sum(a.sentiment_score for a in relevant_articles) / len(relevant_articles)
                    report['market_location_matrix'][key] = {
                        'market': market,
                        'location': location,
                        'article_count': len(relevant_articles),
                        'average_sentiment': round(avg_sentiment, 2),
                        'sentiment_trend': 'positive' if avg_sentiment > 60 else 'negative' if avg_sentiment < 40 else 'neutral'
                    }
        
        return report

async def main():
    """Funzione principale"""
    # Configurazione
    MARKET_AREAS = ['tecnologia', 'finanza', 'energia', 'automotive']
    LOCATIONS = ['italia', 'europa', 'usa', 'cina']
    WEBSITES = [
        'https://www.ansa.it',
        'https://www.repubblica.it',
        'https://www.corriere.it',
        'https://www.ilsole24ore.com'
    ]
    
    all_articles = []
    
    async with MarketAreaCrawler(MARKET_AREAS, LOCATIONS) as crawler:
        for website in WEBSITES:
            try:
                articles = await crawler.analyze_website(website)
                all_articles.extend(articles)
                logger.info(f"Trovati {len(articles)} articoli rilevanti da {website}")
            except Exception as e:
                logger.error(f"Errore nell'analisi di {website}: {e}")
        
        # Genera report
        if all_articles:
            report = crawler.generate_market_report(all_articles)
            
            # Salva risultati
            with open('reports/market_sentiment_report.json', 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            # Mostra summary
            print(f"\n=== MARKET SENTIMENT ANALYSIS REPORT ===")
            print(f"Articoli analizzati: {report['total_articles']}")
            print(f"Timestamp: {report['timestamp']}")
            
            print(f"\n--- SENTIMENT PER MERCATO ---")
            for market, data in report['markets'].items():
                print(f"{market.upper()}: {data['average_sentiment']:.1f} ({data['sentiment_trend']}) - {data['article_count']} articoli")
            
            print(f"\n--- SENTIMENT PER LOCALITÀ ---")
            for location, data in report['locations'].items():
                print(f"{location.upper()}: {data['average_sentiment']:.1f} ({data['sentiment_trend']}) - {data['article_count']} articoli")
            
            print(f"\n--- MATRICE MERCATO-LOCALITÀ ---")
            for key, data in report['market_location_matrix'].items():
                print(f"{data['market'].upper()} in {data['location'].upper()}: {data['average_sentiment']:.1f} ({data['sentiment_trend']}) - {data['article_count']} articoli")
            
            print(f"\nReport completo salvato in: reports/market_sentiment_report.json")
        else:
            print("Nessun articolo rilevante trovato.")

if __name__ == "__main__":
    asyncio.run(main())
