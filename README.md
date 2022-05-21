# kvScraper
 
A python script which uses selenium undetected chromedriver, PostrgreSQL database, TELEGRAM API, reCaptcha V2 Verification.

Continiously checks new ads from the brokers' website, if a new ad appears, it sends a letter on the website to the owner of the property.

If the message was sent successfully, uses TELEGRAM API, BOT to send notification to the client as telegram message, containiing all info about the new ad.

Avoids detection of CloudFlare's I'm Under Attack Mode (IUAM), Bypasses Google's reCaptacha v2
