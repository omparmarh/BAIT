#!/usr/bin/env python3
"""
BAIT PRO ULTIMATE - API Integrations Hub
- Spotify music control
- Gmail email management
- Google Calendar events
- Weather information
- News feeds
- OAuth2 authentication
"""

import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

# Try API libraries
try:
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth
    HAS_SPOTIFY = True
except ImportError:
    HAS_SPOTIFY = False
    logging.warning("spotipy not available")

try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    HAS_GOOGLE = True
except ImportError:
    HAS_GOOGLE = False
    logging.warning("Google API libraries not available")

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    logging.warning("requests not available")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# SPOTIFY INTEGRATION
# ═══════════════════════════════════════════════════════════════

class SpotifyIntegration:
    """
    Spotify music control
    """
    
    SCOPES = [
        'user-read-playback-state',
        'user-modify-playback-state',
        'user-read-currently-playing',
        'playlist-read-private',
        'user-library-read'
    ]
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str = 'http://localhost:8888/callback'):
        """
        Initialize Spotify integration
        
        Args:
            client_id: Spotify app client ID
            client_secret: Spotify app client secret
            redirect_uri: OAuth redirect URI
        """
        if not HAS_SPOTIFY:
            raise ImportError("spotipy required for Spotify integration")
        
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        
        self.sp = None
        self._authenticate()
        
        logger.info("Spotify Integration initialized")
    
    def _authenticate(self):
        """Authenticate with Spotify"""
        try:
            auth_manager = SpotifyOAuth(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                scope=' '.join(self.SCOPES)
            )
            
            self.sp = spotipy.Spotify(auth_manager=auth_manager)
            logger.info("Spotify authenticated")
        except Exception as e:
            logger.error(f"Spotify authentication error: {e}")
            self.sp = None
    
    def play(self, uri: Optional[str] = None):
        """
        Start playback
        
        Args:
            uri: Optional Spotify URI (track, playlist, album)
        """
        if not self.sp:
            logger.error("Spotify not authenticated")
            return
        
        try:
            if uri:
                self.sp.start_playback(uris=[uri] if 'track' in uri else None, context_uri=uri if 'track' not in uri else None)
            else:
                self.sp.start_playback()
            logger.info(f"Started playback: {uri or 'resume'}")
        except Exception as e:
            logger.error(f"Playback error: {e}")
    
    def pause(self):
        """Pause playback"""
        if not self.sp:
            return
        
        try:
            self.sp.pause_playback()
            logger.info("Paused playback")
        except Exception as e:
            logger.error(f"Pause error: {e}")
    
    def next_track(self):
        """Skip to next track"""
        if not self.sp:
            return
        
        try:
            self.sp.next_track()
            logger.info("Skipped to next track")
        except Exception as e:
            logger.error(f"Next track error: {e}")
    
    def previous_track(self):
        """Go to previous track"""
        if not self.sp:
            return
        
        try:
            self.sp.previous_track()
            logger.info("Went to previous track")
        except Exception as e:
            logger.error(f"Previous track error: {e}")
    
    def set_volume(self, volume: int):
        """
        Set volume
        
        Args:
            volume: Volume level (0-100)
        """
        if not self.sp:
            return
        
        volume = max(0, min(100, volume))
        
        try:
            self.sp.volume(volume)
            logger.info(f"Set volume to {volume}%")
        except Exception as e:
            logger.error(f"Volume error: {e}")
    
    def search(self, query: str, type: str = 'track', limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search Spotify
        
        Args:
            query: Search query
            type: Search type (track, playlist, album, artist)
            limit: Max results
            
        Returns:
            List of results
        """
        if not self.sp:
            return []
        
        try:
            results = self.sp.search(q=query, type=type, limit=limit)
            
            items = results.get(f'{type}s', {}).get('items', [])
            
            formatted = []
            for item in items:
                formatted.append({
                    'name': item.get('name'),
                    'uri': item.get('uri'),
                    'type': type,
                    'artists': [a['name'] for a in item.get('artists', [])] if type == 'track' else None
                })
            
            return formatted
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    def get_current_track(self) -> Optional[Dict[str, Any]]:
        """Get currently playing track"""
        if not self.sp:
            return None
        
        try:
            current = self.sp.current_playback()
            if not current or not current.get('item'):
                return None
            
            item = current['item']
            return {
                'name': item['name'],
                'artists': [a['name'] for a in item['artists']],
                'album': item['album']['name'],
                'is_playing': current['is_playing'],
                'progress_ms': current['progress_ms'],
                'duration_ms': item['duration_ms']
            }
        except Exception as e:
            logger.error(f"Get current track error: {e}")
            return None

# ═══════════════════════════════════════════════════════════════
# GMAIL INTEGRATION
# ══════════════════════════════════════════════════════════════

class GmailIntegration:
    """
    Gmail email management
    """
    
    SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
    
    def __init__(self, credentials_path: str = 'credentials.json', token_path: str = 'token.json'):
        """
        Initialize Gmail integration
        
        Args:
            credentials_path: Path to OAuth credentials JSON
            token_path: Path to save/load auth token
        """
        if not HAS_GOOGLE:
            raise ImportError("Google API libraries required")
        
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        
        self._authenticate()
        
        logger.info("Gmail Integration initialized")
    
    def _authenticate(self):
        """Authenticate with Gmail"""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
        
        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    logger.error(f"Credentials file not  found: {self.credentials_path}")
                    return
                
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save token
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('gmail', 'v1', credentials=creds)
        logger.info("Gmail authenticated")
    
    def send_email(self, to: str, subject: str, body: str) -> bool:
        """
        Send email
        
        Args:
            to: Recipient email
            subject: Email subject
            body: Email body
            
        Returns:
            True if successful
        """
        if not self.service:
            return False
        
        try:
            import base64
            from email.mime.text import MIMEText
            
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            self.service.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()
            
            logger.info(f"Sent email to {to}")
            return True
        except Exception as e:
            logger.error(f"Send email error: {e}")
            return False
    
    def get_unread_count(self) -> int:
        """Get count of unread emails"""
        if not self.service:
            return 0
        
        try:
            results = self.service.users().messages().list(
                userId='me',
                labelIds=['UNREAD'],
                maxResults=1
            ).execute()
            
            return results.get('resultSizeEstimate', 0)
        except Exception as e:
            logger.error(f"Get unread count error: {e}")
            return 0
    
    def get_recent_emails(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """Get recent emails"""
        if not self.service:
            return []
        
        try:
            results = self.service.users().messages().list(
                userId='me',
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            emails = []
            for msg in messages:
                detail = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['From', 'Subject', 'Date']
                ).execute()
                
                headers = {h['name']: h['value'] for h in detail['payload']['headers']}
                
                emails.append({
                    'id': msg['id'],
                    'from': headers.get('From'),
                    'subject': headers.get('Subject'),
                    'date': headers.get('Date')
                })
            
            return emails
        except Exception as e:
            logger.error(f"Get emails error: {e}")
            return []

# ═══════════════════════════════════════════════════════════════
# WEATHER INTEGRATION
# ═══════════════════════════════════════════════════════════════

class WeatherIntegration:
    """
    Weather information
    """
    
    def __init__(self, api_key: str):
        """
        Initialize weather integration
        
        Args:
            api_key: OpenWeatherMap API key
        """
        if not HAS_REQUESTS:
            raise ImportError("requests required for weather")
        
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5"
        
        logger.info("Weather Integration initialized")
    
    def get_current_weather(self, location: str) -> Optional[Dict[str, Any]]:
        """
        Get current weather
        
        Args:
            location: City name or coordinates
            
        Returns:
            Weather data
        """
        try:
            url = f"{self.base_url}/weather"
            params = {
                'q': location,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'location': data['name'],
                'temp': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'description': data['weather'][0]['description'],
                'humidity': data['main']['humidity'],
                'wind_speed': data['wind']['speed']
            }
        except Exception as e:
            logger.error(f"Weather error: {e}")
            return None
    
    def get_forecast(self, location: str, days: int = 5) -> List[Dict[str, Any]]:
        """Get weather forecast"""
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'q': location,
                'appid': self.api_key,
                'units': 'metric',
                'cnt': days * 8  # 8 forecasts per day
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            forecasts = []
            for item in data['list']:
                forecasts.append({
                    'datetime': item['dt_txt'],
                    'temp': item['main']['temp'],
                    'description': item['weather'][0]['description']
                })
            
            return forecasts
        except Exception as e:
            logger.error(f"Forecast error: {e}")
            return []

# ═══════════════════════════════════════════════════════════════
# API INTEGRATION MANAGER
# ═══════════════════════════════════════════════════════════════

class APIIntegrationManager:
    """
    Manages all API integrations
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize API manager
        
        Args:
            config: Configuration with API keys
        """
        self.config = config
        self.integrations = {}
        
        self._initialize_integrations()
        
        logger.info("API Integration Manager initialized")
    
    def _initialize_integrations(self):
        """Initialize available integrations"""
        # Spotify
        if HAS_SPOTIFY and self.config.get('spotify'):
            try:
                self.integrations['spotify'] = SpotifyIntegration(
                    client_id=self.config['spotify']['client_id'],
                    client_secret=self.config['spotify']['client_secret']
                )
            except Exception as e:
                logger.error(f"Spotify init error: {e}")
        
        # Gmail
        if HAS_GOOGLE and self.config.get('gmail'):
            try:
                self.integrations['gmail'] = GmailIntegration(
                    credentials_path=self.config['gmail'].get('credentials_path', 'credentials.json')
                )
            except Exception as e:
                logger.error(f"Gmail init error: {e}")
        
        # Weather
        if HAS_REQUESTS and self.config.get('weather'):
            try:
                self.integrations['weather'] = WeatherIntegration(
                    api_key=self.config['weather']['api_key']
                )
            except Exception as e:
                logger.error(f"Weather init error: {e}")
    
    def get_integration(self, name: str) -> Optional[Any]:
        """Get integration by name"""
        return self.integrations.get(name)
    
    def list_available(self) -> List[str]:
        """List available integrations"""
        return list(self.integrations.keys())

# ═══════════════════════════════════════════════════════════════
# TESTING
# ═══════════════════════════════════════════════════════════════

def main():
    """Standalone testing"""
    print("=" * 60)
    print("BAIT API Integrations - Test Mode")
    print("=" * 60)
    
    # Example configuration
    config = {
        'weather': {
            'api_key': 'YOUR_OPENWEATHER_API_KEY'
        }
    }
    
    manager = APIIntegrationManager(config)
    
    print(f"\n📦 Available integrations: {manager.list_available()}")
    
    # Test weather if available
    weather = manager.get_integration('weather')
    if weather:
        print("\n🌤️  Testing weather...")
        # current = weather.get_current_weather('London')
        # print(f"  Weather: {current}")
        print("  (Requires valid API key)")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
