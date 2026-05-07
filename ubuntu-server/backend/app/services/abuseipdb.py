import os
import requests
from dotenv import load_dotenv

load_dotenv()

def check_ip(ip_address: str) -> dict:
    api_key = os.getenv("ABUSEIPDB_API_KEY")
    if not api_key or "your_api_key_here" in api_key:
        return {"error": "API key not configured", "threat_score": 0}

    url = 'https://api.abuseipdb.com/api/v2/check'
    querystring = {
        'ipAddress': ip_address,
        'maxAgeInDays': '90'
    }
    headers = {
        'Accept': 'application/json',
        'Key': api_key
    }

    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=5)
        response.raise_for_status()
        data = response.json().get('data', {})
        return {
            "threat_score": data.get("abuseConfidenceScore", 0),
            "country_code": data.get("countryCode", "Unknown"),
            "domain": data.get("domain", "Unknown"),
            "total_reports": data.get("totalReports", 0)
        }
    except Exception as e:
        return {"error": str(e), "threat_score": 0}
