# Supermarket webscraper
## background information
website to scrape food items from the 5 most popular UK supermarkets and display them for easy price comparison. 
This is not a finished product and I am an inexperienced programmer so I am always looking for advice
## installation
???
download the requirements.txt

in static folder add folders for sainsbury's, tesco, aldi and morrisons
## usage
to run use: python manage.py runserver
on a browser visit localhost:8000
enter what you want to look for
## To do
- improve the display template and just the whole look of the website entirely 
- handle cases where no items are found
- looks like sometimes even when the bottom has been reached, tesco's images still havent been loaded in, add some sort of wait, really cant figure this one out. very annoying because the tesco function is currently the bottle neck for speed and i can't make it faster without solving this.
- find out why x and y are being passed to the url when a search is launched

- make good readme