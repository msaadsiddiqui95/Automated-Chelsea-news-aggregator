import os
import json
import requests
import tweepy
import time
from datetime import datetime, timedelta

class ChelseaNewsBot:
    def __init__(self):
        # Twitter API setup
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        
        # Initialize Twitter client
        self.client = tweepy.Client(
            bearer_token=self.bearer_token,
            consumer_key=self.api_key,
            consumer_secret=self.api_secret,
            access_token=self.access_token,
            access_token_secret=self.access_token_secret,
            wait_on_rate_limit=True
        )
        
        # Journalist configuration with their Twitter user IDs
        self.journalists = {
            'FabrizioRomano': {
                'user_id': '330262748',
                'emoji': '🚨',
                'hashtags': '#CFC #Chelsea #TransferNews #HereWeGo',
                'handle': 'FabrizioRomano'
            },
            'DavidOrnstein': {
                'user_id': '300043285',
                'emoji': '⚡',
                'hashtags': '#CFC #Chelsea #BBCSport #TransferNews',
                'handle': 'DavidOrnstein'
            },
            'MattLaw_DT': {
                'user_id': '224554792',
                'emoji': '🔥',
                'hashtags': '#CFC #Chelsea #Telegraph #Blues',
                'handle': 'MattLaw_DT'
            },
            'SimonJohnson_i': {
                'user_id': '1169712447',
                'emoji': '📰',
                'hashtags': '#CFC #Chelsea #TheAthletic #Blues',
                'handle': 'SimonJohnson_i'
            },
            'DiMarzio': {
                'user_id': '114603314',
                'emoji': '🇮🇹',
                'hashtags': '#CFC #Chelsea #TransferNews #SerieA',
                'handle': 'DiMarzio'
            }
        }
        
        # Chelsea keywords for filtering
        self.chelsea_keywords = [
            'chelsea', 'cfc', 'blues', 'stamford bridge', 'cobham',
            'chelseafc', 'ktbffh'
        ]
        
        # Load last processed tweets
        self.last_tweets = self.load_last_tweets()
        
    def load_last_tweets(self):
        """Load last processed tweet IDs"""
        try:
            with open('last_tweets.json', 'r') as f:
                return json.load(f)
        except:
            return {}
            
    def save_last_tweets(self):
        """Save last processed tweet IDs"""
        with open('last_tweets.json', 'w') as f:
            json.dump(self.last_tweets, f, indent=2)
            
    def is_chelsea_related(self, text):
        """Check if tweet is about Chelsea"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.chelsea_keywords)
        
    def format_repost(self, journalist_key, tweet_text, tweet_id):
        """Format tweet for reposting"""
        journalist = self.journalists[journalist_key]
        
        # Clean the text
        clean_text = tweet_text.strip()
        
        # Create the repost
        repost = f"{journalist['emoji']} {clean_text}\n\n"
        repost += f"via @{journalist['handle']} {journalist['hashtags']}\n\n"
        repost += f"https://twitter.com/{journalist['handle']}/status/{tweet_id}"
        
        # Make sure it's under 280 characters
        if len(repost) > 280:
            # Truncate the main text
            max_text_length = 200  # Leave room for the rest
            clean_text = clean_text[:max_text_length] + "..."
            repost = f"{journalist['emoji']} {clean_text}\n\n"
            repost += f"via @{journalist['handle']} {journalist['hashtags']}\n\n"
            repost += f"https://twitter.com/{journalist['handle']}/status/{tweet_id}"
            
        return repost
        
    def post_to_twitter(self, content):
        """Post to Twitter"""
        try:
            response = self.client.create_tweet(text=content)
            print(f"✅ Posted tweet successfully!")
            return True
        except Exception as e:
            print(f"❌ Error posting: {e}")
            return False
            
    def monitor_journalist(self, journalist_key):
        """Monitor one journalist"""
        journalist = self.journalists[journalist_key]
        handle = journalist['handle']
        
        print(f"🔍 Checking {handle}...")
        
        try:
            # Get recent tweets
            tweets = self.client.get_users_tweets(
                id=journalist['user_id'],
                max_results=5,
                tweet_fields=['created_at']
            )
            
            if not tweets.data:
                print(f"No tweets found for {handle}")
                return
                
            for tweet in tweets.data:
                tweet_id = str(tweet.id)
                
                # Skip if already processed
                if journalist_key in self.last_tweets:
                    if tweet_id == str(self.last_tweets[journalist_key]):
                        break
                        
                # Check if it's about Chelsea
                if self.is_chelsea_related(tweet.text):
                    print(f"🔥 Found Chelsea tweet from {handle}!")
                    print(f"Text: {tweet.text[:100]}...")
                    
                    # Format and post
                    formatted_tweet = self.format_repost(journalist_key, tweet.text, tweet_id)
                    
                    if self.post_to_twitter(formatted_tweet):
                        # Save this tweet ID as processed
                        self.last_tweets[journalist_key] = tweet_id
                        print(f"✅ Successfully reposted from {handle}")
                        break
                        
        except Exception as e:
            print(f"❌ Error checking {handle}: {e}")
            
    def run(self):
        """Main function"""
        print(f"🚀 Chelsea News Bot running at {datetime.now()}")
        
        # Check each journalist
        for journalist_key in self.journalists.keys():
            self.monitor_journalist(journalist_key)
            time.sleep(1)  # Small delay
            
        # Save progress
        self.save_last_tweets()
        print("✅ Monitoring complete!")

if __name__ == "__main__":
    bot = ChelseaNewsBot()
    bot.run()
