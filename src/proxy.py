import os
import re
import time
from typing import List, Optional, Dict
import requests
from dataclasses import dataclass


@dataclass
class ProxyUsage:
    proxy: str
    last_used: float


class ProxyService:
    proxies: List[ProxyUsage] = []
    initialized: bool = False
    proxy_username: str = os.getenv('PROXY_USERNAME', '')
    proxy_password: str = os.getenv('PROXY_PASSWORD', '')
    last_initialize_time: float = 0

    @classmethod
    def initialize(cls) -> None:
        cls.last_initialize_time = time.time()
        if cls.initialized:
            return

        proxies_path = os.path.join(os.getcwd(), './data/proxies.txt')
        proxy_url = os.getenv('PROXY_DOWNLOAD_LINK')

        if not proxy_url:
            print('PROXY_DOWNLOAD_LINK is not set in environment variables.')
            cls.proxies = []
            exit(1)
        
        try:
            # Download proxies from URL
            print('Downloading proxies from webshare.io...')
            response = requests.get(proxy_url)
            if not response.ok:
                raise Exception(f'Failed to download proxies: {response.status_code} {response.reason}')
            content = response.text
            
            # Save to proxies.txt
            with open(proxies_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print('Proxies downloaded and saved to proxies.txt')
            
            # Parse proxy list
            proxy_list = []
            for line in content.split('\n'):
                line = line.strip()
                if len(line) > 0:
                    # Extract IP:Port from formats like:
                    # 'http://username:password@193.187.114.167:6182:username:password'
                    # Result: '193.187.114.167:6182'
                    match = re.search(r'(\d+\.\d+\.\d+\.\d+:\d+)', line)
                    if match:
                        proxy_list.append(match.group(1))
                    else:
                        proxy_list.append(line)

            cls.proxies = [ProxyUsage(proxy=proxy, last_used=0) for proxy in proxy_list]

            cls.initialized = True
            print(f'Loaded {len(cls.proxies)} proxies')
        except Exception as error:
            print(f'Error loading proxies: {error}')
            cls.proxies = []

    @classmethod
    def get_oldest_used_proxy(cls) -> Optional[str]:
        if time.time() - cls.last_initialize_time > 12 * 60 * 60:
            cls.initialize()

        if not cls.initialized:
            cls.initialize()

        if len(cls.proxies) == 0:
            print('No proxies available')
            return None

        # Sort by last_used timestamp (ascending) to get the oldest used proxy
        cls.proxies.sort(key=lambda x: x.last_used)

        oldest_proxy = cls.proxies[0]
        oldest_proxy.last_used = time.time()

        # Add authentication credentials to proxy
        # Format: http://username:password@host:port
        proxy_with_auth = f'http://{cls.proxy_username}:{cls.proxy_password}@{oldest_proxy.proxy}'

        return proxy_with_auth

    @classmethod
    def get_proxy_count(cls) -> int:
        if not cls.initialized:
            cls.initialize()
        return len(cls.proxies)

    @classmethod
    def reset_usage_times(cls) -> None:
        for p in cls.proxies:
            p.last_used = 0