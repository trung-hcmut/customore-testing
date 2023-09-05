import unittest
from playwright_plus.utils.exceptions import catch_TimeoutError
from playwright._impl._api_types import TimeoutError as PlaywrightTimeoutError


class TestCatchTimeoutError(unittest.TestCase):

    '''----------------------------------test_create_block_resources()-------------------------------------------'''
    '''
    Test function test_create_block_resources():

    - Case : Customize Data 
      - Input:
        - exception_class: CustomTimeoutErrorException
        - message :"func: customize timeout error"

      - Expected Output:
        - after the function execution, the exception will be raised and the message has the same value with message passed.
    '''

    def test_catch_timeout_error_decorator(self):
        class CustomTimeoutErrorException(Exception):
            message = "function_with_timeout_error"

        @catch_TimeoutError(exception_class=CustomTimeoutErrorException, message="func: customize timeout error")
        def function_with_timeout_error():
            raise PlaywrightTimeoutError("Timeout occurred")

        try:
            # Call the decorated function
            function_with_timeout_error()
        except CustomTimeoutErrorException as custom_exception:
            print(str(custom_exception))
            # Check if the custom exception was raised with the expected message
            self.assertEqual(
                str(custom_exception),
                "func: customize timeout error",
            )


if __name__ == "__main__":
    unittest.main()
