import unittest
from unittest.mock import Mock, MagicMock
from playwright.sync_api import Page
from playwright_plus.browser_surf import (
    create_block_resources,
    open_new_page,
    with_page,
    wait_after_execution,
    check_for_loaded_marker,
)


class TestBrowserSurf(unittest.TestCase):

    def setUp(self):
        # Create a mock Page object for testing
        self.page = MagicMock(spec=Page)

    '''----------------------------------test_create_block_resources()-------------------------------------------'''
    '''
    Test function test_create_block_resources():
  
    Create block_resources = [...]

    - Case 1: Valid Data 
      - Input:
        - resource_type in block_resources

      - Expected Output:
        - .abort() function is called succesfully

    - Case 2: Error Data 
      - Input:
        - resource_type not in block_resources

      - Expected Output:
        - .abort() function is not called
        - .continue_() function is called successfully
    '''

    def test_create_block_resources_valid_data(self):
        # Test blocking image and stylesheet resources
        block_resources = create_block_resources(["image", "stylesheet"])

        mock_route = Mock()
        mock_route.request.resource_type = "image"
        block_resources(mock_route)
        self.assertTrue(mock_route.abort.called)

    def test_create_block_resources_error_data(self):
        block_resources = create_block_resources(["image", "stylesheet"])

        mock_route = Mock()
        mock_route.request.resource_type = "script"
        block_resources(mock_route)
        self.assertFalse(mock_route.abort.called)
        self.assertTrue(mock_route.continue_.called)

    '''----------------------------------test_open_new_page()-------------------------------------------'''
    '''
    Test function test_open_new_page():

    - Case 1: Default settings 
      - Input:
        - None

      - Expected Output:
        - browser, context, page are not equal None
        - page will be closed after function ran finished (page.is_closed() is True)

    - Case 2: Customize settings 
      - Input:
        - Various parameters, including proxy_info, headless, accept_downloads, block_resources, ...etc

      - Expected Output:
        - browser, context, page are not equal None
        - after the function execution, the page should be closed (page.is_closed() is True)
    '''

    def test_open_new_page_with_default_settings(self):
        browser, context, page = open_new_page()
        self.assertIsNotNone(browser)
        self.assertIsNotNone(context)
        self.assertIsNotNone(page)
        # self.assertTrue(page.is_closed())

    def test_open_new_page_with_customize_settings(self):
        proxy_info = {"server": "http://google.com"}
        browser, context, page = open_new_page(
            proxy_info=proxy_info,
            headless=False,
            accept_downloads=False,
            block_resources=["image"],
        )
        print(f'DEBUG MODE: {browser}, {context}, {page}')
        self.assertIsNotNone(browser)
        self.assertIsNotNone(context)
        self.assertIsNotNone(page)
        # self.assertTrue(page.is_closed())

    '''----------------------------------with_page() decorator-------------------------------------------'''
    '''
    Test decorator with_page():

        - Case: 
            - Input:
                - various parameters, including headless, accept_downloads, block_resources,... etc

            - Expected Output:
                - the decorator should open a browser, context, and page based on the provided configuration arguments.
                - the decorated function should be executed with the open page.
                - after the function execution, the page should be closed (page.is_closed() is True)

    '''

    def test_with_page_decorator(self):
        # Define a sample function to be decorated
        @with_page(headless=False, accept_downloads=True, block_resources=False)
        def sample_function(page):
            # self.assertIsNotNone(page)
            # self.assertTrue(page.is_closed())
            pass

        # Call the decorated function
        sample_function()

    '''----------------------------------wait_after_execution()-------------------------------------------'''
    '''
    Test function wait_after_execution():
        - Case 1: Default settings
            - Input:
                - None
            
            - Expected output:
                - The decorator should execute the decorated function, and a randomized time within a 15% range. (because in this time, randomized is True)

        - Case 2: Customize settings
            - Input:
                - wait_ms: 10,000
                - randomized: False
                - or kwargs or func_args has "wait_ms"
            
            - Expected output:
                - Reason: we tried to use rand_int(), so we should test it multiple time.
                - The decorator should execute the decorated function and then wait for the specified time (wait_ms - if have)
                or a randomized time should have at least once time not within a 15% range. (because in this time, randomized is False)

    '''

    '''----------------------------------check_for_loaded_marker()-------------------------------------------'''
    '''
    Test function check_for_loaded_marker():
        - Case 1: Default settings
            - Input:
                - None
            
            - Expected output:
                - The decorator should wait for the specified marker to become visible on the web page before executing the decorated function.

        - Case 2: Customize settings
            - Input:
                - marker: CSS Element | "top"
                - marker_strict: True
                - load_message : "testing"
                - timeout: 100,000
            
            - Expected output:
                - The decorator should wait for the specified marker to become visible on the web page before executing the decorated function.
                - After the function execution, the decorator should continue to wait 10 seconds for the marker.
 
    '''


if __name__ == "__main__":
    unittest.main()
