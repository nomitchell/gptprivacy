import trafilatura

downloaded = trafilatura.fetch_url('https://www.amazon.com/gp/help/customer/display.html?nodeId=GX7NJQ4ZB8MHFRNJ')
text = trafilatura.extract(downloaded)
print(text)