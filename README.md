# kvScraper
 
A python webscraper script which uses selenium undetected chromedriver, BeautifulSoup, PostgreSQL database, TELEGRAM API, Bypasses Google's reCaptcha V2 Verification, CloudFlare's I'm Under Attack Mode (IUAM)

Continiously checks new ads from the brokers' website, if a new ad appears, it sends a letter on the website to the owner of the property.

If the message was sent successfully, uses TELEGRAM API, BOT to send confirm notification to the client as telegram message, containing all info about the new ad, real estate google map link, real estate owners phone, name.

Avoids detection of CloudFlare's I'm Under Attack Mode (IUAM), Bypasses Google's reCaptacha v2
