"""
Synthetic Enterprise Authentication Log & Threat Pattern Generator
"""
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from cyberguard.config.settings import RAW_DATA_DIR
from cyberguard.utils.logger import get_logger

logger = get_logger("generator")

# Geo Reference Data
COUNTRY_COORDS = {
    "US": {"lat": 37.0902, "lon": -95.7129, "cities": ["New York", "San Francisco", "Chicago"]},
    "IN": {"lat": 20.5937, "lon": 78.9629, "cities": ["Bangalore", "Mumbai", "Delhi"]},
    "JP": {"lat": 36.2048, "lon": 138.2529, "cities": ["Tokyo", "Osaka"]},
    "GB": {"lat": 55.3781, "lon": -3.4360, "cities": ["London", "Manchester"]},
    "FR": {"lat": 46.2276, "lon": 2.2137, "cities": ["Paris", "Lyon"]},
    "DE": {"lat": 51.1657, "lon": 10.4515, "cities": ["Berlin", "Frankfurt"]},
    "AU": {"lat": -25.2744, "lon": 133.7751, "cities": ["Sydney", "Melbourne"]},
    "RU": {"lat": 61.5240, "lon": 105.3188, "cities": ["Moscow", "Saint Petersburg"]},
    "CN": {"lat": 35.8617, "lon": 104.1954, "cities": ["Beijing", "Shanghai"]},
    "BR": {"lat": -14.2350, "lon": -51.9253, "cities": ["Sao Paulo", "Rio de Janeiro"]}
}

DEVICE_TYPES = ["Workstation-Windows", "Laptop-macOS", "Server-Linux", "Mobile-iOS", "Mobile-Android"]
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/16.4",
    "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 Chrome/120.0.0.0"
]

NORMAL_USERS = [f"user_{i}" for i in range(1, 30)]
ADMIN_USERS = ["root", "admin", "sysadmin"]

def generate_synthetic_auth_logs(num_records: int = 1500, random_seed: int = 42) -> pd.DataFrame:
    """
    Generate realistic enterprise authentication logs with embedded threat vectors:
    - Normal authentications
    - Brute force bursts
    - Impossible travel sequences
    - Credential stuffing
    - Privilege escalation
    """
    np.random.seed(random_seed)
    random.seed(random_seed)
    logger.info(f"Generating {num_records} synthetic authentication logs...")

    start_time = datetime(2026, 7, 1, 8, 0, 0)
    records = []
    
    # 1. Normal Baseline Traffic (~75% of events)
    normal_count = int(num_records * 0.75)
    for _ in range(normal_count):
        dt = start_time + timedelta(seconds=random.randint(0, 86400 * 5))
        user = random.choice(NORMAL_USERS)
        country = random.choice(["US", "IN", "JP", "GB", "FR", "DE", "AU"])
        geo = COUNTRY_COORDS[country]
        lat = geo["lat"] + random.uniform(-1.0, 1.0)
        lon = geo["lon"] + random.uniform(-1.0, 1.0)
        city = random.choice(geo["cities"])
        ip = f"{random.randint(10, 200)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
        status = "Success" if random.random() > 0.12 else "Failed"
        device = random.choice(DEVICE_TYPES)
        user_agent = random.choice(USER_AGENTS)
        
        records.append({
            "timestamp": dt.strftime("%Y-%m-%d %H:%M:%S"),
            "username": user,
            "ip_address": ip,
            "country": country,
            "city": city,
            "latitude": round(lat, 4),
            "longitude": round(lon, 4),
            "status": status,
            "device_type": device,
            "user_agent": user_agent,
            "attack_label": "Normal"
        })

    # 2. Embedded Threat Scenario: Brute Force Bursts
    # Specific user experiences 15 rapid failed logins from same IP
    brute_user = "user_7"
    brute_ip = "185.220.101.5"
    brute_time = start_time + timedelta(hours=14, minutes=30)
    for i in range(18):
        records.append({
            "timestamp": (brute_time + timedelta(seconds=i * 12)).strftime("%Y-%m-%d %H:%M:%S"),
            "username": brute_user,
            "ip_address": brute_ip,
            "country": "RU",
            "city": "Moscow",
            "latitude": 55.7558,
            "longitude": 37.6173,
            "status": "Failed",
            "device_type": "Workstation-Windows",
            "user_agent": USER_AGENTS[0],
            "attack_label": "Brute Force"
        })
    # Final successful login after brute force (Account Takeover)
    records.append({
        "timestamp": (brute_time + timedelta(seconds=18 * 12 + 5)).strftime("%Y-%m-%d %H:%M:%S"),
        "username": brute_user,
        "ip_address": brute_ip,
        "country": "RU",
        "city": "Moscow",
        "latitude": 55.7558,
        "longitude": 37.6173,
        "status": "Success",
        "device_type": "Workstation-Windows",
        "user_agent": USER_AGENTS[0],
        "attack_label": "Brute Force"
    })

    # 3. Embedded Threat Scenario: Impossible Travel
    # Same user logs in from US (San Francisco) and 10 mins later from JP (Tokyo)
    travel_user = "user_12"
    t1 = start_time + timedelta(days=2, hours=10)
    records.append({
        "timestamp": t1.strftime("%Y-%m-%d %H:%M:%S"),
        "username": travel_user,
        "ip_address": "12.145.22.8",
        "country": "US",
        "city": "San Francisco",
        "latitude": 37.7749,
        "longitude": -122.4194,
        "status": "Success",
        "device_type": "Laptop-macOS",
        "user_agent": USER_AGENTS[1],
        "attack_label": "Normal"
    })
    records.append({
        "timestamp": (t1 + timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S"),
        "username": travel_user,
        "ip_address": "133.242.18.90",
        "country": "JP",
        "city": "Tokyo",
        "latitude": 35.6762,
        "longitude": 139.6503,
        "status": "Success",
        "device_type": "Server-Linux",
        "user_agent": USER_AGENTS[2],
        "attack_label": "Impossible Travel"
    })

    # 4. Embedded Threat Scenario: Credential Stuffing
    # Single malicious IP tries 25 different usernames
    stuff_ip = "45.154.255.88"
    stuff_time = start_time + timedelta(days=3, hours=4)
    for idx, u in enumerate(random.sample(NORMAL_USERS, 20)):
        records.append({
            "timestamp": (stuff_time + timedelta(seconds=idx * 8)).strftime("%Y-%m-%d %H:%M:%S"),
            "username": u,
            "ip_address": stuff_ip,
            "country": "CN",
            "city": "Beijing",
            "latitude": 39.9042,
            "longitude": 116.4074,
            "status": "Failed" if idx < 18 else "Success",
            "device_type": "Workstation-Windows",
            "user_agent": USER_AGENTS[0],
            "attack_label": "Credential Stuffing"
        })

    # 5. Embedded Threat Scenario: Privilege Escalation Attempt
    priv_ip = "198.51.100.42"
    priv_time = start_time + timedelta(days=1, hours=22)
    for adm in ADMIN_USERS:
        for i in range(4):
            records.append({
                "timestamp": (priv_time + timedelta(seconds=(i+1)*15)).strftime("%Y-%m-%d %H:%M:%S"),
                "username": adm,
                "ip_address": priv_ip,
                "country": "BR",
                "city": "Sao Paulo",
                "latitude": -23.5505,
                "longitude": -46.6333,
                "status": "Failed",
                "device_type": "Server-Linux",
                "user_agent": USER_AGENTS[2],
                "attack_label": "Privilege Escalation"
            })

    df = pd.DataFrame(records)
    # Sort chronologically
    df["dt_temp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values(by="dt_temp").drop(columns=["dt_temp"]).reset_index(drop=True)
    
    logger.info(f"Successfully generated {len(df)} authentication records with threats.")
    return df

def save_synthetic_dataset(output_path: Path = None) -> Path:
    if output_path is None:
        output_path = RAW_DATA_DIR / "auth_logs.csv"
    df = generate_synthetic_auth_logs(num_records=1500)
    df.to_csv(output_path, index=False)
    logger.info(f"Saved auth logs dataset to {output_path}")
    return output_path

if __name__ == "__main__":
    save_synthetic_dataset()
