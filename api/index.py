import os
import requests
from flask import Flask, jsonify
from firecrawl import FirecrawlApp
from dotenv import load_dotenv
import datetime

load_dotenv()

app = Flask(__name__)

# Initialize Firecrawl
firecrawl_api_key = os.getenv('fc-70ea2858608f4ca4844db97246b3e562')
firecrawl_app = FirecrawlApp(api_key=firecrawl_api_key)

def scrape_replit_bounties():
    """Scrape Replit bounties using Firecrawl"""
    url = "https://replit.com/bounties?status=open&order=creationDateDescending"
    
    try:
        # Scrape the page
        scraped_data = firecrawl_app.scrape_url(url)
        
        # Extract relevant information (adjust based on actual Firecrawl response structure)
        bounties = []
        if scraped_data and 'data' in scraped_data and 'content' in scraped_data['data']:
            # This is a simplified example - you'll need to parse the actual HTML content
            # or use Firecrawl's LLM extraction if available
            content = scraped_data['data']['content']
            
            # Here you would add parsing logic for the actual bounty data
            # This is a placeholder - you'll need to inspect the page structure
            # and adjust the parsing accordingly
            bounties.append({
                'title': 'Sample Bounty',
                'price': '$500',
                'url': 'https://replit.com/bounties/1'
            })
            
        return bounties
    
    except Exception as e:
        print(f"Error scraping Replit bounties: {e}")
        return []

def format_bounties(bounties):
    """Format bounties into a Slack message"""
    if not bounties:
        return "No new bounties found."
    
    message = "*🔥 New Replit Bounties Available! 🔥*\n\n"
    for bounty in bounties:
        message += f"• <{bounty['url']}|{bounty['title']}> - {bounty['price']}\n"
    
    message += f"\n_Last updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}_"
    return message

def send_to_slack(message):
    """Send message to Slack via webhook"""
    slack_webhook = os.getenv('https://hooks.slack.com/services/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')
    if not slack_webhook:
        print("SLACK_WEBHOOK_URL not set")
        return False
    
    payload = {
        "text": message
    }
    
    try:
        response = requests.post(slack_webhook, json=payload)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Error sending to Slack: {e}")
        return False

@app.route('/')
def home():
    return "Replit Bounty Bot is running!"

@app.route('/scrape-and-notify', methods=['POST'])
def scrape_and_notify():
    """Endpoint to trigger scraping and notification"""
    bounties = scrape_replit_bounties()
    message = format_bounties(bounties)
    success = send_to_slack(message)
    
    return jsonify({
        "status": "success" if success else "error",
        "message": "Notification sent to Slack" if success else "Failed to send notification",
        "bounties_count": len(bounties)
    })

if __name__ == '__main__':
    app.run(debug=True)
