import requests as r
import logging
import functools

foldl = lambda func, acc, xs: functools.reduce(func, xs, acc)

class RunescapePricesAPI():
    base_endpoint = "https://prices.runescape.wiki/api/v1/osrs/"
    items_endpoint = 'mapping'
    price_endpoint_per_id = f'{base_endpoint}/latest?id='

    headers = {
        'User-Agent': 'Mozilla/5.0',
        'From': 'fatilluch@gmail.com'  # This is another valid field
    }

    def __init__(self):
        self.total_per_page = 10

    def get_all_items(self):
        """ Makes an API request to the given endpoint and returns a dictionary containing the data
    #     Returns:
    #         dict: data drawn from the given endpoint
    #     """
        return self.make_request(self.base_endpoint + self.items_endpoint, [])

    def get_price_data(self, id):
        """Fetches price-related data for a given element.

        Args:
            id (int): The ID of the element.

        Returns:
            dict or None: A dictionary containing price data for the element if available,
                          or None if there's a connection error.

        This function attempts to retrieve price-related data for a specific element
        identified by its ID. It sends a request to the price API endpoint using the
        provided ID, retrieves the data, and if available, structures it into a dictionary
        with 'highPrice', 'highTime', 'lowPrice', 'lowTime', and 'profit_margin' keys.
        In case of a connection error, it prints an error message and returns None.
        """
        price_response = self.make_request(f'{self.price_endpoint_per_id}{id}')
        price_data = price_response['data']
        if bool(price_data):
            return {
                'highPrice': price_data[str(id)]['high'],
                'highTime': price_data[str(id)]['highTime'],
                'lowPrice': price_data[str(id)]['low'],
                'lowTime': price_data[str(id)]['lowTime'],
                'profit_margin': price_data[str(id)]['high'] - price_data[str(id)]['low']
            }
        return None

    def get_paged_items_prices(self, page):
        items_data = self.get_all_items()
        total_items = len(items_data)
        elements_per_page = self.get_data_per_page(items_data, page)
        total_pages = (total_items + self.total_per_page - 1) // self.total_per_page

        page = max(min(page, total_pages), 1)

        start_page = max(min(page - self.total_per_page // 2, total_pages - self.total_per_page + 1), 1)
        end_page = min(start_page + self.total_per_page, total_pages + 1)
        return foldl(self.fetch_element_price_data, [], elements_per_page)

    def fetch_element_price_data(self, acc, element):
        price_data = self.get_price_data(element['id'])
        if price_data:
            element.update(price_data)
            acc.append(element)
        return acc

    def get_data_per_page(self, items, page):
        """Gets the data per page


        Args:
            element (list): sublist of the total number element belonging to the API Call
            page (int): actual page number
            total_per_page (int): amount of elements that are being contained in one page

        Returns:
            list: a list of elements
        """
        try:
            start = (page - 1) * self.total_per_page
            end = start + self.total_per_page
            return items[start:end]
        except Exception as e:
            logging.error(f"Error occurred in get_data_per_page: {e}")
            return None

    def make_request(self, endpoint, default_return_value=[]):
        """
        Initiates a GET request to the provided URL.

        Args:
            endpoint (str): The URL to which the GET request will be sent.

        This function performs a GET request to the specified `endpoint`.
        It uses the `requests.get()` method to make the request and prints the URL before
        initiating the request. Upon receiving the response, it checks the HTTP status code;
        if it's 200 (OK), it logs a successful request message using the Python `logging` module.
        In case of any connection errors during the request, it logs an error message with
        details of the encountered exception.
        :param endpoint:
        :param default_return_value:
        """
        try:
            response = r.get(endpoint, headers=self.headers)
            if 200 <= response.status_code < 300:
                logging.info(f"Successful Request to {endpoint}")
                data = response.json()
                if not data:
                    return default_return_value
                return data
            else:
                logging.info(f"Error Requesting to {endpoint}")
                return None
        except r.RequestException as e:
            logging.error(f'There was a connection error: {e}', exc_info=True)
            logging.error(f"Connection Error to {endpoint}: {e}")
            raise e
