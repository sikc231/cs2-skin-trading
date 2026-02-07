from .proxy import ProxyService
import requests

class csfloatItems:
    def __init__(self, max_price: float, min_price: float):
        self.max_price = max_price
        self.min_price = min_price
        self.NewOffersQeuryLink = "https://csfloat.com/api/v1/listings?limit=50&sort_by=most_recent&min_price=" + str(self.min_price) + "&max_price=" + str(self.max_price) + "&type=buy_now"
        self.BestOffersQueryLink = "https://csfloat.com/api/v1/listings?limit=50&sort_by=best_deal&min_price=" + str(self.min_price) + "&max_price=" + str(self.max_price) + "&type=buy_now"

    def fetch_deals(self):
        print("Fetching Deals...")
        proxy = ProxyService.get_oldest_used_proxy()
        print("Using Proxy:", proxy)
        
        # Setup proxy for requests
        proxies = {
            'http': proxy,
            'https': proxy
        }
        
        try:
            # Fetch new offers
            print(f"\nFetching New Offers from: {self.NewOffersQeuryLink}")
            new_offers_response = requests.get(self.NewOffersQeuryLink, proxies=proxies)
            new_offers_response.raise_for_status()
            new_offers_data = new_offers_response.json()
            print("New Offers Response:")
            print(new_offers_data)
            
            # Fetch best offers
            print(f"\nFetching Best Offers from: {self.BestOffersQueryLink}")
            best_offers_response = requests.get(self.BestOffersQueryLink, proxies=proxies)
            best_offers_response.raise_for_status()
            best_offers_data = best_offers_response.json()
            print("Best Offers Response:")
            print(best_offers_data)
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching deals: {e}")