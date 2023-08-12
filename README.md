# <Underground Mixology>

## Description

Cocktail recipe database driven website using https://www.thecocktaildb.com/api.php. Built using Flask, SQLAlchemy, Jinja, JQuery and WTForms

## Installation

-   Create app directory and virtual environment, activating source

-   Clone repo https://github.com/Brinzkii/Capstone-Project.git

-   Install req's with 'pip install -r requirements.txt'

-   Start databases with 'sudo service postgresql start'

-   Create database with 'createdb capstone'

## Seeding

Seeding the database takes awhile due to the number of requests necessary and the delay needed between each to get successful responses. Be prepared to wait 30 minutes - you will get status updates via the console throughout the process

-   Run ipython

-   '%run seed.py'

## Testing

-  Create database with 'createdb capstone-test'

-  All tests can be run with 'python -m unittest'

-  Specific test files can be run with 'python -m unittest file_name.py'

## Usage

-   Start flask with 'flask run'

-   Enter localhost:5000/ in browser
