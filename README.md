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

- get quantity from websites, easy with asda, morrisons and aldi (they have a specific element for it)
but with sainsburys and tesco they put quantity at the end of name
IDEA find the index of the last space and get the rest of the string from that point. however, this wont work for milk because tesco has e.g. '4 pints' so this method would get only 'pints'

hack idea, for pints/litres use pythons rindex() to find the index of the last space then use this as a pattern to replace it:
    a = "4 pints"
    b = a.rindex(' ')
    c = a[:b] + a[b+1:]
then use use above IDEA and get the quantity, otherwise i will have to use regex
- make good readme