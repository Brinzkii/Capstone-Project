# <Underground Mixology>

## Description

Underground Mixology is a drink recipe database driven website built with Flask, SQLAlchemy, Jinja, JQuery and WTForms. The Cockatail API (https://www.thecocktaildb.com/api.php) was used to add initial 577 drink recipes.

Deployed @ https://ug-mixology.onrender.com/

## Features

-   If logged in and favorites exist, random drinks containing matching ingredients will be suggested on the homepage. If logged in and no favorites exist, random drinks will be suggested.

-   Search for drink name, category or ingredient

-   View drinks by category

-   View drinks by glass type

-   Save and share favorite recipes

-   Add/edit/delete drink recipes

-   Leave comments on drink recipes

-   See total likes and comments for each drink

-   View other users favorites and drink posts

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
