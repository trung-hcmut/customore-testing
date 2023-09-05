import unittest
from unittest.mock import MagicMock
from playwright.sync_api import Page
from playwright_plus.web_intercept import (
    set_json_to_page,
    construct_handle_response,
    intercept_json_playwright,
    intercept_json_playwright_old,
    intercept_json_playwright_multiple,
    request_json_playwright
)


class TestWebIntercept(unittest.TestCase):
    def setUp(self):
        # Create a mock Page object for testing
        self.page = MagicMock(spec=Page)

    '''----------------------------------set_json_to_page()-------------------------------------------'''
    '''
    Test function set_json_to_page():
  
    - Case 1: Valid JSON Data - test_set_json_to_page_valid_data()
      - Input:
        - page: a Playwright Page object.
        - buffer: a dictionary containing valid JSON data.

      - Expected Output:
        - page.target_json should be populated with the provided JSON data.

    - Case 2: Error Data  - test_set_json_to_page_error_data()
      - Input:
        - page: a Playwright Page object.
        - buffer: a dictionary containing error information.

      - Expected Output:
        - page.target_json should include the error information.
    '''

    def test_set_json_to_page_valid_data(self):
        # Test setting valid JSON data to a Page object
        buffer_data = {"data": {"test_key": "test_value"}}
        set_json_to_page(self.page, buffer_data)

        # Assert that page.target_json is correctly populated
        self.assertEqual(self.page.target_json, {
                         "data": {"test_key": "test_value"}})

    def test_set_json_to_page_error_data(self):
        # Test setting error data to a Page object
        buffer_data = {"data": {}, "error": "Error message"}
        set_json_to_page(self.page, buffer_data)

        # Assert that page.target_json includes error information
        self.assertEqual(
            self.page.target_json,
            {
                "error": "PlaywrightInterceptError",
                "error_message": "Error message",
                "data": {},
            },
        )

    '''----------------------------------construct_handle_response()----------------------------------------'''
    '''
    Test function construct_handle_response()

      - Case 1: Matching URL Subpart - test_construct_handle_response_matching_url_subpart()
        - Input:
          - response: a Playwright Response object with a URL that matches the specified json_url_subpart.

        - Expected Output:
          - The response should be processed, and the relevant data should be extracted.

      -Case 2: Non-Matching URL Subpart - test_construct_handle_response_non_matching_url_subpart()
        - Input:
          - response: a Playwright Response object with a URL that does not match the specified json_url_subpart.

        - Expected Output:
          - The response should not be processed, and the data should remain unchanged.
    '''

    def test_construct_handle_response_matching_url_subpart(self):
        # Test the decorator function with a response that matches the URL subpart
        page = MagicMock(spec=Page)
        response = MagicMock()
        response.url = "https://jsonplaceholder.typicode.com/posts/1"

        handle_response = construct_handle_response(page, "/posts/1")
        handle_response(response)

        # give assert here

    def test_construct_handle_response_non_matching_url_subpart(self):
        # Test the decorator function with a response that does not match the URL subpart
        page = MagicMock(spec=Page)
        response = MagicMock()
        response.url = "https://jsonplaceholder.typicode.com/posts/1"

        handle_response = construct_handle_response(page, "/posts/2")
        handle_response(response)

        # give assert here

    '''----------------------------------intercept_json_playwright()-----------------------------------------'''
    '''
    Test function intercept_json_playwright()

    - Case 1: Valid JSON Response
      - Input:
        - various parameters, including page_url, json_url_subpart, and valid JSON response data.

      - Expected Output:
        - The function should correctly intercept and return the valid JSON data.

    - Case 2: Error Detection
      - Input:
        - various parameters, including page_url, json_url_subpart, and JSON response data with an error.

      - Expected Output:
        - The function should detect the error and include it in the result.

    - Case 3: CAPTCHA Handling
      - Input:
        - various parameters, including page_url, json_url_subpart, and simulated CAPTCHA challenge.

      - Expected Output:
        - The function should handle the CAPTCHA challenge and return the data if solved.

    - Case 4: Timeout Handling
      - Input:
        - various parameters, including page_url, json_url_subpart, and a timeout value.

      - Expected Output:
        - If the timeout is reached without intercepting valid JSON, the function should return an appropriate error.

    - Case 5: Multiple Refreshes
      - Input:
        - various parameters, including page_url, json_url_subpart, and a scenario requiring multiple page refreshes.

      - Expected Output:
        - The function should correctly handle the multiple refreshes and return the data.
    '''

    def test_intercept_json_playwright_valid_response(self):
        # Test intercepting a valid JSON response
        page_url = "https://jsonplaceholder.typicode.com"
        json_url_subpart = "/posts/1"
        json_data = {"key": "value"}

        # Mock page.goto and page.on to simulate response interception
        self.page.goto.return_value = None
        self.page.on.side_effect = [
            MagicMock(url=page_url),
            MagicMock(url=f"{page_url}{json_url_subpart}", json=json_data),
        ]

        result = intercept_json_playwright(
            page_url, json_url_subpart, page=self.page)
        print("Result: ", result)

        # Assert that the function correctly intercepts and returns the valid JSON data
        # self.assertEqual(
        #     result, {"error": None, "error_message": None, "data": json_data})

    # other case will be handled in the next time
    # WILL TO DO

    '''----------------------------------intercept_json_playwright_old()-----------------------------------------'''
    '''
    Test function intercept_json_playwright_old()

    - Case 1: Valid JSON Response
      - Input:
        - various parameters, including page_url, json_url_subpart, and valid JSON response data.

      - Expected Output:
        - The function should correctly intercept and return the valid JSON data.

    - Case 2: Error Detection
      - Input:
        - various parameters, including page_url, json_url_subpart, and JSON response data with an error.

      - Expected Output:
        - The function should detect the error and include it in the result.

    - Case 3: Timeout Handling
      - Input:
        - various parameters, including page_url, json_url_subpart, and a timeout value.

      - Expected Output:
        - If the timeout is reached without intercepting valid JSON, the function should return an appropriate error.

    '''

    def test_intercept_json_playwright_old_valid_response(self):
        # Test intercepting a valid JSON response
        page_url = "https://jsonplaceholder.typicode.com"
        json_url_subpart = "/posts/1"
        json_data = {"key": "value"}

        # Mock page.goto and page.on to simulate response interception
        self.page.goto.return_value = None
        self.page.on.side_effect = [
            MagicMock(url=page_url),
            MagicMock(url=f"{page_url}{json_url_subpart}", json=json_data),
        ]

        result = intercept_json_playwright_old(
            page_url, json_url_subpart, page=self.page)

        # Assert that the function correctly intercepts and returns the valid JSON data
        # self.assertEqual(
        #     result, {"error": None, "error_message": None, "data": json_data})

    '''-----------------------------------intercept_json_playwright_multiple()----------------------------------------'''
    '''
    Test function intercept_json_playwright_multiple()

      - Case 1: Single JSON Response
        - Input:
          - various parameters, including page_url, json_url_subpart, and a single JSON response.

        - Expected Output:
          - The function should correctly intercept and return the single JSON response.

      - Case 2: Multiple JSON Responses
        - Input:
          - various parameters, including page_url, json_url_subpart, and multiple JSON responses with expect_more set to a value greater than 1.

        - Expected Output:
          - The function should correctly intercept and return all the JSON responses.

      - Case 3: Error Detection
        - Input:
          - various parameters, including page_url, json_url_subpart, and JSON responses with errors.

        - Expected Output:
          - The function should detect the errors and include them in the result.

      - Case 4: Timeout Handling    
        - Input:
          - various parameters, including page_url, json_url_subpart, and a timeout value.

        - Expected Output:
          - If the timeout is reached without intercepting valid JSON, the function should return an appropriate error.
    '''

    '''-----------------------------------request_json_playwright()---------------------------------------'''
    '''
    Test function request_json_playwright()
      - Case 1: Valid JSON Request
        - Input:
          - json_url: URL of a JSON endpoint with valid JSON data.

        - Expected Output:
          - The function should send a request, intercept the valid JSON response, and return the JSON data.

      - Case 2: Error Detection
        - Input:
          - json_url: URL of a JSON endpoint that returns an error response.

        - Expected Output:
          - The function should detect the error and include it in the result.

      - Case 3: Timeout Handling
        - Input:
          - json_url: URL of a JSON endpoint with a timeout set.

        - Expected Output:
          - If the timeout is reached without intercepting valid JSON, the function should return an appropriate error.

    '''


if __name__ == "__main__":
    unittest.main()
