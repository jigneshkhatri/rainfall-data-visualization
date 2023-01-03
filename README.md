Visualize the rainfall data on the map in grid format on any area around the world. Apart from rainfall data visualization, these scripts can be used for following purposes:
- Visualize any other data related to location on the map in grid format
- To divide the area on the map in grid with required single cell size (area)

# Environment
- Python: v3.9

# Setup `pipenv`
- If not installed, install `pipenv` using below command:
    - `pip install pipenv`
- Setup reference: https://pipenv.pypa.io/en/latest/install/

### Install dependencies:
- `pipenv install`
- Install specific dependency:
    - `pipenv install <lib name>`

# How to run?
- Create an account and get the API key from any of the below weather data providers:
    - https://www.visualcrossing.com/
    - https://www.worldweatheronline.com/
    - This is required to fetch the rainfall data according to lat-lon and dates passed
    - Depending on which data provider you choose, change the method which is called from `set_rainfall_data(..)` method in `generate_datasets.py` script
- Run `generate_datasets.py` script with the params (check the script source for exact params and their details)
    - This will generate the rainfall datasets under `resources/datasets` directory
- Once the datasets are generated, run `app.py` to visualize the data
