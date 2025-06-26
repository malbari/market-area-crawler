#!/usr/bin/env python3
"""
Script per eseguire il Market Area Crawler
"""

import asyncio
import json
import sys
from datetime import datetime
from main import MarketAreaCrawler
from config import MARKET_AREAS, LOCATIONS, WEBSITES


async def run_analysis():
    """Esegue l'analisi completa"""
    print("=== MARKET AREA CRAWLER - SENTIMENT ANALYSIS ===")
    print(f"Avvio analisi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Mercati monitorati: {', '.join(MARKET_AREAS)}")
    print(f"Località monitorate: {', '.join(LOCATIONS)}")
    print(f"Siti da analizzare: {len(WEBSITES)}")
    print("-" * 50)

    all_articles = []

    async with MarketAreaCrawler(MARKET_AREAS, LOCATIONS) as crawler:
        for i, website in enumerate(WEBSITES, 1):
            try:
                print(f"[{i}/{len(WEBSITES)}] Analizzando: {website}")
                articles = await crawler.analyze_website(website)
                all_articles.extend(articles)
                print(f"  → Trovati {len(articles)} articoli rilevanti")
            except Exception as e:
                print(f"  → Errore: {e}")

        print("-" * 50)

        if all_articles:
            print(f"Totale articoli rilevanti: {len(all_articles)}")
            print("Generando report...")

            report = crawler.generate_market_report(all_articles)

            # Salva report dettagliato
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'market_sentiment_{timestamp}.json'

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)

            # Salva anche gli articoli per riferimento
            articles_data = []
            for article in all_articles:
                articles_data.append({
                    'title':
                    article.title,
                    'url':
                    article.url,
                    'market_areas':
                    article.market_areas,
                    'locations':
                    article.locations,
                    'sentiment_score':
                    article.sentiment_score,
                    'content_preview':
                    article.content[:200] +
                    '...' if len(article.content) > 200 else article.content
                })

            articles_filename = f'articles_{timestamp}.json'
            with open(articles_filename, 'w', encoding='utf-8') as f:
                json.dump(articles_data, f, ensure_ascii=False, indent=2)

            # Mostra summary
            print_summary(report)
            print(f"\nFile generati:")
            print(f"  • Report: {filename}")
            print(f"  • Articoli: {articles_filename}")

        else:
            print("❌ Nessun articolo rilevante trovato.")
            print("Suggerimenti:")
            print("  • Verifica le keyword in config.py")
            print("  • Controlla la connessione internet")
            print("  • Alcuni siti potrebbero bloccare il crawler")


def print_summary(report):
    """Stampa un summary del report"""
    print("\n" + "=" * 60)
    print("📊 SUMMARY SENTIMENT ANALYSIS")
    print("=" * 60)

    print(f"📅 Timestamp: {report['timestamp']}")
    print(f"📰 Articoli totali: {report['total_articles']}")

    if report['markets']:
        print(f"\n🏭 SENTIMENT PER MERCATO:")
        for market, data in report['markets'].items():
            trend_emoji = "📈" if data[
                'sentiment_trend'] == 'positive' else "📉" if data[
                    'sentiment_trend'] == 'negative' else "➡️"
            print(
                f"  {trend_emoji} {market.upper()}: {data['average_sentiment']:.1f}/100 ({data['article_count']} articoli)"
            )

    if report['locations']:
        print(f"\n🌍 SENTIMENT PER LOCALITÀ:")
        for location, data in report['locations'].items():
            trend_emoji = "📈" if data[
                'sentiment_trend'] == 'positive' else "📉" if data[
                    'sentiment_trend'] == 'negative' else "➡️"
            print(
                f"  {trend_emoji} {location.upper()}: {data['average_sentiment']:.1f}/100 ({data['article_count']} articoli)"
            )

    if report['market_location_matrix']:
        print(f"\n🎯 TOP CORRELAZIONI MERCATO-LOCALITÀ:")
        # Ordina per sentiment score
        sorted_matrix = sorted(report['market_location_matrix'].items(),
                               key=lambda x: x[1]['average_sentiment'],
                               reverse=True)

        for i, (key, data) in enumerate(sorted_matrix[:5]):  # Top 5
            trend_emoji = "📈" if data[
                'sentiment_trend'] == 'positive' else "📉" if data[
                    'sentiment_trend'] == 'negative' else "➡️"
            print(
                f"  {i+1}. {trend_emoji} {data['market'].upper()} in {data['location'].upper()}: {data['average_sentiment']:.1f}/100"
            )


if __name__ == "__main__":
    try:
        asyncio.run(run_analysis())
    except KeyboardInterrupt:
        print("\n❌ Analisi interrotta dall'utente")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Errore durante l'analisi: {e}")
        sys.exit(1)
