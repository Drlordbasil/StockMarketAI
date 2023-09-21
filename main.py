import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import time


class StockMarketAnalyzer:
    def __init__(self):
        self.base_url = "https://www.examplestockmarketwebsite.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }

    def scrape_stock_price(self, stock_symbol):
        url = f"{self.base_url}/stocks/{stock_symbol}"
        try:
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, "html.parser")
            price_element = soup.find("span", class_="stock-price")
            if price_element:
                return price_element.text.strip()
            else:
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching stock price: {e}")
            return None

    def scrape_trading_volume(self, stock_symbol):
        url = f"{self.base_url}/stocks/{stock_symbol}"
        try:
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, "html.parser")
            volume_element = soup.find("span", class_="trading-volume")
            if volume_element:
                return volume_element.text.strip()
            else:
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching trading volume: {e}")
            return None

    def scrape_company_news(self, stock_symbol):
        url = f"{self.base_url}/news/{stock_symbol}"
        try:
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, "html.parser")
            news_articles = soup.find_all("div", class_="news-article")
            news_list = []
            for article in news_articles:
                title = article.find("h2").text.strip()
                summary = article.find("p").text.strip()
                news_list.append({"title": title, "summary": summary})
            return news_list
        except requests.exceptions.RequestException as e:
            print(f"Error fetching company news: {e}")
            return []

    def scrape_historical_data(self, stock_symbol, start_date, end_date):
        url = f"{self.base_url}/historical/{stock_symbol}?start={start_date}&end={end_date}"
        try:
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, "html.parser")
            data_table = soup.find("table", class_="historical-data")
            data_rows = data_table.find_all("tr")[1:]
            data_list = []
            for row in data_rows:
                columns = row.find_all("td")
                date = columns[0].text.strip()
                open_price = float(columns[1].text.strip())
                high_price = float(columns[2].text.strip())
                low_price = float(columns[3].text.strip())
                close_price = float(columns[4].text.strip())
                volume = int(columns[5].text.strip().replace(",", ""))
                data_list.append(
                    {
                        "Date": date,
                        "Open": open_price,
                        "High": high_price,
                        "Low": low_price,
                        "Close": close_price,
                        "Volume": volume,
                    }
                )
            return pd.DataFrame(data_list)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching historical data: {e}")
            return pd.DataFrame()

    def analyze_stock_trends(self, stock_symbol, start_date, end_date):
        data = self.scrape_historical_data(stock_symbol, start_date, end_date)
        data["Date"] = pd.to_datetime(data["Date"])
        data.set_index("Date", inplace=True)

        # Generate line chart
        plt.plot(data.index, data["Close"])
        plt.title(f"{stock_symbol} Stock Price")
        plt.xlabel("Date")
        plt.ylabel("Closing Price")
        plt.show()

        # Generate candlestick chart
        fig, ax = plt.subplots()
        ax.plot(data.index, data["High"], color="green", label="High")
        ax.plot(data.index, data["Low"], color="red", label="Low")
        ax.plot(data.index, data["Close"], color="black", label="Close")
        ax.plot(data.index, data["Open"], color="blue", label="Open")
        ax.legend()
        ax.set_title(f"{stock_symbol} Stock Price")
        ax.set_xlabel("Date")
        ax.set_ylabel("Price")
        plt.show()

        # Generate histogram of daily returns
        returns = data["Close"].pct_change().dropna()
        plt.hist(returns, bins=30)
        plt.title(f"{stock_symbol} Daily Returns")
        plt.xlabel("Returns")
        plt.ylabel("Frequency")
        plt.show()

    def manage_portfolio(self, portfolio):
        current_date = datetime.date.today().strftime("%Y-%m-%d")
        portfolio_value = 0
        for stock_symbol, stock_info in portfolio.items():
            stock_price = float(self.scrape_stock_price(stock_symbol))
            if stock_price:
                quantity = stock_info["quantity"]
                stock_value = stock_price * quantity
                portfolio_value += stock_value
                print(
                    f"{stock_symbol}: {quantity} shares, Current Price: {stock_price}, Value: {stock_value}"
                )

        print(f"Total Portfolio Value on {current_date}: {portfolio_value}")

    def set_price_alert(self, stock_symbol, price_threshold):
        while True:
            stock_price = float(self.scrape_stock_price(stock_symbol))
            if stock_price >= price_threshold:
                print(
                    f"Alert: Current price of {stock_symbol} is above the set threshold of {price_threshold}"
                )
                break
            time.sleep(60)  # Check the price every minute


if __name__ == "__main__":
    analyzer = StockMarketAnalyzer()

    stock_symbol = "AAPL"
    trading_volume = analyzer.scrape_trading_volume(stock_symbol)
    if trading_volume:
        print(f"{stock_symbol} Trading Volume: {trading_volume}")
    else:
        print("Error fetching trading volume.")

    news_articles = analyzer.scrape_company_news(stock_symbol)
    if news_articles:
        print("Latest News Articles:")
        for article in news_articles:
            print(f"Title: {article['title']}")
            print(f"Summary: {article['summary']}")
            print()
    else:
        print("Error fetching company news.")

    start_date = "2021-01-01"
    end_date = "2021-12-31"
    analyzer.analyze_stock_trends(stock_symbol, start_date, end_date)

    portfolio = {
        "AAPL": {"quantity": 10},
        "GOOG": {"quantity": 5},
        "TSLA": {"quantity": 2},
    }
    analyzer.manage_portfolio(portfolio)

    stock_symbol = "AMZN"
    price_threshold = 3500.0
    analyzer.set_price_alert(stock_symbol, price_threshold)
