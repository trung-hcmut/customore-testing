# Built-in imports
from copy import deepcopy
import logging
import time

# Public 3rd party packages imports
from playwright.sync_api._generated import Page, Locator

# Private packages imports
from playwright_plus import with_page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from asyncio.exceptions import CancelledError

# Local functions and relative imports
# Constants imports
# New constants

# This file contains function to scrape a web page by simulating a browser surfing


def set_json_to_page(page, buffer):
    '''
    Sets the 'target_json' attribute of a Playwright 'page' based on the provided 'buffer' data.

    This function is used to manage the 'target_json' attribute of a Playwright 'page' object based on the contents of
    the provided 'buffer' dictionary and allow to handling data received during interactions with web pages and
    handling potential errors.

    - Args:
        page (object, required)        : a Playwright Page_ object to associate with the 'target_json' data.
        buffer (object, required)      : a dictionary containing data, possibly including error information.

    - Returns:
        None

    - How to use
        example

        buffer_data = {"data": {}, "error": "error"}
        set_json_to_page(page, buffer_data)

    '''

    if not buffer.get("error"):
        page.target_json = buffer
    else:
        page.target_json = {
            "error": "PlaywrightInterceptError",
            "error_message": buffer["error"],
            "data": {},
        }


def construct_handle_response(page: Page, json_url_subpart: str):
    '''
    Decorator function for handling responses during web page interactions.

    - Args:
        page (Page): a Playwright Page object representing the web page context
        json_url_subpart (str): A string representing a subpart of the URL to match for processing

    - Returns:
        callable: a callable function (handle_response) that handles responses during web page interactions

    - How to use:
        example

        @construct_handle_response(page, "/api/data")
        def customize_func(response):
            pass

        customize_func(response)

    '''
    def handle_response(response):
        try:
            if json_url_subpart in response.url:
                try:
                    buffer = response.json()
                except Exception as jde:
                    buffer = {
                        "error": f"exception when trying to intercept:{str(jde)}"}

                set_json_to_page(page, buffer)

        except CancelledError:
            logging.debug("handle_response was correctly canceled")

    return handle_response


@with_page(headless=True)
def intercept_json_playwright(
    page_url: str,
    json_url_subpart: str,
    page: Page = None,
    json_detect_error: callable = None,
    json_parse_result: callable = None,
    captcha_solver_function: callable = None,
    max_refresh: int = 1,
    timeout: int = 4000,
    goto_timeout=30000,
    **kwargs,
) -> dict:
    '''
    Intercepts JSON responses from a web page and processes them using Playwright.

    This function automates web page interactions and intercepts JSON responses from a specified URL subpart.

    - Args:
        page_url (str, required)                    : the URL of the web page to interact with.
        json_url_subpart (str, required)            : a subpart of the URL to match for intercepting JSON responses.
        page (Page, optional)                       : a Playwright 'Page' object representing the web page context. 
                                                    If not provided, it will be automatically injected by the '@with_page' decorator.
            Default value is None
        json_detect_error (callable, optional)      : a callable function that can be used to detect errors in the intercepted JSON data. 
                                                    It should accept a 'result' dictionary and return a tuple containing a boolean 
                                                    indicating whether an error is detected and the modified 'result' dictionary.
            Default value is None
        json_parse_result (callable, optional)      : a callable function to parse the intercepted JSON data. It should
                                                    accept the 'result' dictionary and return the parsed data.
        captcha_solver_function (callable, optional): A callable function for solving CAPTCHA challenges if they are
                                                    encountered during web interactions. It should accept the Page object 
                                                    and return a tuple containing a boolean indicating whether a CAPTCHA was solved 
                                                    and whether a page refresh is required.
            Default value is None
        max_refresh (int, optional)                 : the maximum number of page refreshes allowed to resolve issues. 
            Default value is 1
        timeout (int, optional)                     : the maximum time (in milliseconds) to wait for JSON responses to be intercepted.
            Default is 4,000 ms (4 seconds)
        goto_timeout (int, optional)                : the maximum time (in milliseconds) to wait for the initial page load. 
            Default is 30,000 ms (30 seconds)
        kwargs                                      : Additional keyword arguments for configuring the browser and page behavior.

    - Returns:
        dict                                        : A dictionary containing the intercepted JSON data or error information.

    - How to use:
        example

        @with_page(headless=True)
        def my_json_interceptor(page):
            result = intercept_json_playwright(
                page_url="https://jsonplaceholder.typicode.com/posts",
                json_url_subpart="/posts",
                page=page,
                json_detect_error=customize_error_detector,
                json_parse_result=customize_result_parser,
                captcha_solver_function=customize_captcha_solver,
                max_refresh=2,
                timeout=8000,
            )

        my_json_interceptor(page)

    '''
    logging.debug("This version of playwright_intercept is deprecated")
    time_spent = 0
    nb_refresh = 0
    captcha_to_solve = False

    # set up the page to intercept the wanted call
    target_json = {}

    def handle_response(response):
        if json_url_subpart in response.url:
            try:
                buffer = response.json()
            except Exception as jde:
                buffer = {
                    "error": f"exception when trying to intercept:{str(jde)}"}

            if not buffer.get("error"):
                target_json["data"] = buffer

            else:
                target_json["data"] = {
                    "error": "PlaywrightInterceptError",
                    "error_message": buffer["error"],
                    "data": {},
                }

    page.on("response", handle_response)

    # call the onsite page
    s = time.time()
    try:
        page.goto(page_url, timeout=goto_timeout)
    except:
        # This should be return error since we can't do anything without our page
        pass
    duration = time.time() - s
    time_spent += int(duration * 1000)

    # wait for the valid json to be intercepted
    while (time_spent <= timeout) and (nb_refresh < max_refresh):
        s = time.perf_counter()

        # get the data that has been intercepted
        target_json = target_json.get("data", {})
        logging.debug(
            f"time_spent : {time_spent}. target_json keys: {target_json.keys()}"
        )

        # Create a result object from the intercepted data
        result = {"error": None, "error_message": None,
                  "data": deepcopy(target_json)}

        # if the proper function was provided, scan the result for error
        is_error = False
        if callable(json_detect_error):
            is_error, result = json_detect_error(result)

        # two known cases of error are possible
        # no json was yet intercepted >> note the error, wait for the next loop iteration
        if not target_json:
            result = {
                "error": "PlaywrightInterceptError",
                "error_message": "An empty json was collected after calling the hidden API.",
                "data": {},
            }

        # A captcha was raised > raise a flag for a captcha to be solved
        elif result.get("error") == "CaptchaRaisedError":
            captcha_to_solve = True

        # Other scenario (no error, or unknown new error)
        else:
            break

        # if a captcha flag was raised, try to solve it
        if captcha_to_solve and callable(captcha_solver_function):
            ask_for_refresh, captcha_solved = captcha_solver_function(page)
            if captcha_solved:
                # reset the json and wait for next interception
                captcha_to_solve = False
                target_json = {}
                result = {}

            if ask_for_refresh:
                try:
                    logging.debug("refresh")
                    nb_refresh += 1
                    ask_for_refresh = False
                    page.goto(page_url, timeout=3000)
                except:
                    pass

        # if this loop iteration was too short, wait more time (total duration must be at least 500ms)
        duration = time.perf_counter() - s
        if duration * 1000 < 500:
            remaining_sleep_time = 500 - int(duration * 1000)
            page.wait_for_timeout(remaining_sleep_time)

        # update the time_spent
        duration = time.perf_counter() - s
        time_spent += duration * 1000

    # if the proper function was provided, parse the intercepted json
    if (not is_error) and json_parse_result:
        result = json_parse_result(result)

    return result


@with_page(headless=True)
def intercept_json_playwright_old(
    page_url: str,
    json_url_subpart: str,
    page: Page = None,
    json_detect_error: callable = None,
    json_parse_result: callable = None,
    wait_seconds: int = 4,
    **kwargs,
) -> dict:
    '''
    Intercepts a JSON response from a specified URL and processes it.

    - Args:
        page_url (str, required)                : the URL to visit and intercept JSON from.
        json_url_subpart (str, required)        : a subpart of the JSON URL to match and intercept.
        page (Page, optional)                   : the Playwright Page object. If None, it will be provided by the @with_page decorator.
            Default value is None
        json_detect_error (callable, optional)  : a custom error detection function. Takes a result dict and returns (is_error, result).
            Default value is None
        json_parse_result (callable, optional)  : a custom result parsing function. Takes a result dict and returns the parsed result.
            Default value is None
        wait_seconds (int, optional)            : the number of seconds to wait for JSON interception.
            Default value is None

    - Returns:
        dict                                    : a dictionary containing the intercepted JSON data and error information if applicable.

    - How to use:
        example

        @with_page(headless=True)
        def custom_json_detect(result):
            if result.get("error"):
                return True, result
            return False, result

        @with_page(headless=True)
        def custom_json_parse(result):
            data = result.get("data")
            if data:
                return {"parsed_data": data}
            return {"parsed_data": None}

        result = intercept_json_playwright_old(
            page_url="",
            json_url_subpart="/api/data",
            json_detect_error=custom_json_detect,
            json_parse_result=custom_json_parse,
            wait_seconds=4
        )

    '''
    target_json = {}

    def handle_response(response):
        try:
            if json_url_subpart in response.url:
                try:
                    buffer = response.json()
                except Exception as jde:
                    buffer = {
                        "error": f"exception when trying to intercept:{str(jde)}"}

                if not buffer.get("error"):
                    target_json["data"] = buffer
                else:
                    target_json["data"] = {
                        "error": "PlaywrightInterceptError",
                        "error_message": buffer["error"],
                        "data": {},
                    }
        except CancelledError:
            logging.debug("handle_response was correctly canceled")

    page.on("response", handle_response)

    try:
        page.goto(page_url)
    except PlaywrightTimeoutError as err:
        return {
            "error": "PlaywrightTimeoutError",
            "error_message": str(err),
            "data": {},
        }
    except Exception as err:
        return {"error": "PlaywrightGotoError", "error_message": str(err), "data": {}}

    for _ in range(wait_seconds * 2):
        page.wait_for_timeout(500)
        target_json = target_json.get("data", {})

        logging.debug(f"target_json keys: {target_json.keys()}")
        if not target_json:
            result = {
                "error": "PlaywrightInterceptError",
                "error_message": "An empty json was collected after calling the hidden API.",
                "data": {},
            }
        else:
            result = {"error": None,
                      "error_message": None, "data": target_json}
            break

    if json_detect_error:
        is_error, result = json_detect_error(result)

    if (not is_error) and json_parse_result:
        result = json_parse_result(result)

    return result


@with_page(headless=True)
def intercept_json_playwright_multiple(
    page_url: str,
    json_url_subpart: str,
    page=None,
    json_detect_error: callable = None,
    json_parse_result: callable = None,
    wait_seconds: int = 4,
    expect_more: int = 0,
    **kwargs,
) -> dict:
    """
    Intercept JSON responses from a web page in a development environment.

    This function is designed for use in a development environment and is used to intercept JSON responses from a web page.
    It waits for JSON responses that match the specified `json_url_subpart` and can handle situations where multiple JSON
    responses are expected.

    - Args:
        page_url (str, required)                : the URL of the web page to visit.
        json_url_subpart (str, required)        : the subpart of the JSON URL to match when intercepting responses.
        page (Page, optional)                   : the Playwright page to use for interception. If not provided, it will be passed 
                                                automatically  by the '@with_page' decorator.
            Default value is None
        json_detect_error (callable, optional)  : a callable function that can be used to detect errors in the intercepted
                                                JSON data. It should accept a 'result' dictionary and return a tuple containing a boolean indicating 
                                                whether an error is detected and the modified 'result' dictionary.
            Default value is None
        json_parse_result (callable, optional)  : a callable function to parse the intercepted JSON data. It should accept
                                                the 'result' dictionary and return the parsed data.
            Default value is None
        wait_seconds (int, optional)            : the number of seconds to wait for JSON responses.
            Default value is 4
        expect_more (int, optional)             : the number of additional JSON responses expected. Use this to handle situations where
                                                multiple JSON responses may be received. It decrements with each expected response.
            Default value is 0

    - Returns:
        dict                                    : a dictionary containing the intercepted JSON data or error information.

    - How to use:
        example

        def customize_error_detector(result):
            # Implement error detection logic here
            return is_error, modified_result

        def customize_result_parser(result):
            # Implement JSON parsing logic here
            return parsed_data

        result = request_json_playwright(
            json_url="https://jsonplaceholder.typicode.com/posts",
            json_detect_error=customize_error_detector,
            json_parse_result=customize_result_parser,
            headless=True,  # Additional keyword arguments for configuring the browser behavior
        )

    ---------------------------------------------------------------------------------------------   

    WARNING this is a dev environement.
    In a future version this will be merged with the other equivalent methods
    This particular variety needs to be able to recieve a wrong API cal and
    wait for a second one.

    ---------------------------------------------------------------------------------------------
    """
    target_json = {}

    def handle_response(response):
        try:
            if json_url_subpart in response.url:
                try:
                    buffer = response.json()
                except Exception as jde:
                    buffer = {
                        "error": f"exception when trying to intercept:{str(jde)}"}

                if not buffer.get("error"):
                    target_json["data"] = buffer
                else:
                    target_json["data"] = {
                        "error": "PlaywrightInterceptError",
                        "error_message": buffer["error"],
                        "data": {},
                    }
        except CancelledError:
            logging.debug("handle_response was correctly canceled")

    page.on("response", handle_response)
    try:
        page.goto(page_url)
    except PlaywrightTimeoutError as err:
        pass
    except Exception as err:
        return {"error": "PlaywrightGotoError", "error_message": str(err), "data": {}}

    # Check if error
    is_error = True
    result = {
        "error": "PlaywrightInterceptError",
        "error_message": "An empty json was collected after calling the hidden API.",
        "data": {},
    }

    for _ in range(wait_seconds * 2):
        page.wait_for_timeout(500)
        target_json = target_json.get("data", {})

        logging.debug(f"target_json keys: {target_json.keys()}")
        if target_json:
            result = {"error": None,
                      "error_message": None, "data": target_json}

            # Check if the result is correct
            if json_detect_error:
                is_error, result = json_detect_error(result)

            if not is_error or expect_more == 0:
                # If we find a correct one or we have recived too many errors
                # We break
                break
            else:
                # If it is an error but we expect more
                # we reduce the total expected
                expect_more -= 1

    if (not is_error) and json_parse_result:
        result = json_parse_result(result)

    return result


def request_json_playwright(
    json_url: str,
    json_detect_error: callable = None,
    json_parse_result: callable = None,
    **kwargs,
) -> dict:
    '''
    Send a request to a JSON endpoint using Playwright and intercept the JSON response.

    This function sends a request to a specified JSON endpoint URL and intercepts the JSON response from the web page.

    - Args:
        json_url (str, required)                : The URL of the JSON endpoint to request data from.
        json_detect_error (callable, optional)  : a callable function that can be used to detect errors in the intercepted
                                                JSON data. It should accept a 'result' dictionary and 
                                                return a tuple containing a boolean indicating whether
                                                an error is detected and the modified 'result' dictionary.
        json_parse_result (callable, optional)  : a callable function to parse the intercepted JSON data. It should accept
                                                the 'result' dictionary and return the parsed data.
        kwargs                                  : Additional keyword arguments for configuring the browser and page behavior, 
                                                as well as other options.

    - Returns:
        dict                                    : A dictionary containing the intercepted JSON data or error information.

    - How to use:
        example

        def customize_error_detector(result):
            return is_error, modified_result

        def customize_result_parser(result):
            return parsed_data

        result = request_json_playwright(
            json_url="https://jsonplaceholder.typicode.com/posts",
            json_detect_error=customize_error_detector,
            json_parse_result=customize_result_parser,
            headless=True,  # Additional keyword arguments for configuring the browser behavior
        )

    '''
    result = intercept_json_playwright(
        page_url=json_url,
        json_url_subpart=json_url,
        json_detect_error=json_detect_error,
        json_parse_result=json_parse_result,
        **kwargs,
    )

    return result
