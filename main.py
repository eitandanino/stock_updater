import os
import requests

# API Keys and Tokens from environment variables
FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
print(f"FINNHUB_API_KEY length: {len(FINNHUB_API_KEY)}")
print(f"TELEGRAM_BOT_TOKEN length: {len(TELEGRAM_BOT_TOKEN)}")


# Tickers to monitor
TICKERS = ["SPY", "QQQ", "DIA", "IWM"]


# Function to check if the market is open
def is_market_open():
    url = f"https://finnhub.io/api/v1/stock/market-status?exchange=US&token={FINNHUB_API_KEY}"
    response = requests.get(url).json()

    # Check if the market is open
    if response.get("isOpen"):
        return True
    return False


# Function to fetch ticker data
def get_ticker_data(ticker):
    url = "https://finnhub.io/api/v1/quote"
    params = {
        "symbol": ticker,
        "token": FINNHUB_API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()
    if "c" in data and "pc" in data:
        current_price = data["c"]
        previous_close = data["pc"]
        percentage_change = ((current_price - previous_close) / previous_close) * 100
        return current_price, previous_close, percentage_change
    else:
        raise Exception(f"Failed to fetch data for {ticker}")


# Function to send Telegram message using `requests`
def send_channel_message(message, channel_username="stockupdate2025"):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    params = {
        "chat_id": f"@{channel_username}",
        "text": message
    }
    requests.get(url, params=params)


# Function to get all unique chat IDs
def get_all_chat_ids():
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    response = requests.get(url).json()

    # Extract chat IDs
    chat_ids = set()  # Use a set to avoid duplicates
    for update in response.get("result", []):
        if "message" in update:
            chat_id = update["message"]["chat"]["id"]
            chat_ids.add(chat_id)
    return list(chat_ids)


# Function to prepare and send daily update
def daily_update():
    try:
        # Check if the market is open
        if not is_market_open():
            print("The market is closed today. Sending notification to users.")
            closed_message = "השוק סגור היום אין עדכונים"
            send_channel_message(closed_message)
            return  # Exit if the market is closed

        # Prepare the message
        messages = []
        for ticker in TICKERS:
            current_price, previous_close, percentage_change = get_ticker_data(ticker)

            # Choose icon based on percentage change
            icon = "📈" if percentage_change >= 0 else "📉"

            message = (
                f"{icon} {ticker} Daily Update:\n"
                f"🔹 Closing Price: ${current_price:.2f}\n"
                f"🔹 Change: {percentage_change:.2f}%"
            )
            messages.append(message)

        # Combine all messages
        final_message = "\n\n".join(messages)
        send_channel_message(final_message)

    except Exception as e:
        error_message = f"❌ Failed to fetch data: {e}"
        print(error_message)


# Run the daily update
daily_update()
