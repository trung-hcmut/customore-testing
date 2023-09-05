# Built-in imports
import logging
from random import randint

# Public 3rd party packages imports
from playwright.sync_api import sync_playwright
from playwright.sync_api._generated import Page, Locator
from asyncio.exceptions import CancelledError

# Private packages imports
# Local functions and relative imports
# Constants imports
# New constants
EXCLUDED_RESOURCES_TYPES = ["stylesheet", "image", "font", "svg"]

__all__ = [
    "check_for_loaded_marker",
    "open_new_page",
    "wait_after_execution",
    "with_page",
]


def create_block_resources(resources_to_block: list):
    '''
    Create a route handler function for blocking the external resource or the specialize resources during web automation time.  

    - Args: 
        resources_to_block (list, requuired)    : a list of resources types to block    
            Type of values needs to into the list values from Playwright's resource type constants (e.g., "image", "stylesheet", "font").   

            See more:   
            - https://playwright.dev/python/docs/api/class-request#request-resource-type    
            - https://www.zenrows.com/blog/blocking-resources-in-playwright#blocking-resources  

    - Return:   
        callable    : a route handler function that can be blocked resource or continued others (based on the input)    

    - How to use:   
        exmaple:    

        ROUTE = "**/*"  
        # create a new page, see: https://playwright.dev/docs/pages 

        page = await context.newPage()  

        block_resources = create_block_resources(["image","font","stylesheet"]) 

        page.route(ROUTE, block_resources)  

    '''

    def _block_resources(route):
        """
         Block or continue resources based on the provided resource types.

        Args:
            route (Route): the route object representing the intercepted request

        Raises:
            CancelledError: if the route handling is canceled

            See more:
            - https://playwright.dev/python/docs/api/class-request#request-resource-type
            - https://www.zenrows.com/blog/blocking-resources-in-playwright#blocking-resources

        """
        try:
            if route.request.resource_type in resources_to_block:
                route.abort()

            else:
                route.continue_()

        except CancelledError as err:
            logging.debug("block_resources was correctly canceled")

    return _block_resources


# WEB BROWSER AND PAGE OPENING

def _instantiate_browser_context_page(
    p,
    proxy_info: dict = None,
    headless: bool = True,
    accept_downloads: bool = True,
    block_resources: bool | list = True,
    cookies: list[dict] = None,
    browser_type: str = "chromium",
    **kwargs,
):
    '''
    Create and configure a browser, context of browser and page of web automation.

    - Args:

        p (Playwright, required)                : the Playwright instance
        proxy_info (dict, optional)             : proxy configuration information
            Default value: None
        headless (boo, optional)                : the checker to run browser in headless mode or not
            Default value: True
        accpet_downloads (bool, optional)       : the checker to accept downloads
            Default value: True
        block_resources (bool | list, optinal)  : Determines if and which resources to block.
            If value was True, it default blocks EXCLUDED_RESOURCES_TYPES.
            If a list is provided, it blocks the specified resource types.
            Default value: True
        cookies (list[dict], optional)          : list cookies will be imported to browser context
            Default value: None
        browser_type (str, optional)            : the type of browser will be launched
            Default value: "chromium"
        kwargs                                   : Additional keyword arguments for configuring the browser and page behavior.


            See more:
            - https://playwright.dev/docs/api/class-browsertype#browser-type-launch
            - https://playwright.dev/python/docs/api/class-browsertype#browser-type-launch

    - Return:

        tuple: a tuple contains information about browser, context and page object

    - How to use:
        example:

        _browser, _context, _page = _instantiate_browser_context_page(
        p,
        proxy_info = {
            "server": "http://resource.com:3000", 
        },
        headless = True,
        browser_type = "firefox",
        )

        page.goto("http://test_local.com")

    '''

    # open chromium browser, using specified proxy
    logging.debug(
        f"[playwright_plus] open a browser : headless={headless}, proxy_info={proxy_info.get('server') if isinstance(proxy_info, dict) else None}"
    )
    match browser_type:
        case "chromium":
            browser = p.chromium.launch(headless=headless, proxy=proxy_info)
        case "firefox":
            browser = p.firefox.launch(headless=headless, proxy=proxy_info)
    # create the browser context
    logging.debug(
        f"[playwright_plus] open a browser context: accept_downloads={accept_downloads}, with {len(cookies) if cookies else 0} cookies set(s)"
    )
    context = browser.new_context(accept_downloads=accept_downloads)
    context.add_init_script(
        """
            navigator.webdriver = false
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false
            })
        """
    )
    if cookies:
        context.add_cookies(cookies)

    # open a web page
    logging.debug(
        f"[playwright_plus] open a new page: blocked resources={EXCLUDED_RESOURCES_TYPES if block_resources==True else block_resources}"
    )
    page = context.new_page()
    if block_resources:
        resources_to_block = (
            EXCLUDED_RESOURCES_TYPES if block_resources == True else block_resources
        )

        def _block_resources(route):
            try:
                if route.request.resource_type in resources_to_block:
                    route.abort()

                else:
                    route.continue_()

            except CancelledError as err:
                logging.debug("block_resources was correctly canceled")

        page.route("**/*", _block_resources)

    return browser, context, page


def open_new_page(
    proxy_info: dict = None,
    headless: bool = True,
    accept_downloads: bool = True,
    block_resources: bool | list = True,
    cookies: list[dict] = None,
    **kwargs,
):
    '''
    Open a new browser page with configurations for web automation.

    - Args:

        proxy_info (dict, optional)             : proxy configuration information
            Default value: None
        headless (boo, optional)                : the checker to run browser in headless mode or not
            Default value: True
        accpet_downloads (bool, optional)       : the checker to accept downloads
            Default value: True
        block_resources (bool | list, optinal)  : Determines if and which resources to block.
            If value was True, it default blocks EXCLUDED_RESOURCES_TYPES.
            If a list is provided, it blocks the specified resource types.
            Default value: True
        cookies (list[dict], optional)          : list cookies will be imported to browser context
            Default value: None
        kwargs                                  : Additional keyword arguments for configuring the browser and page behavior.


            See more:
            - https://playwright.dev/docs/api/class-browsertype#browser-type-launch

    - Return:

        tuple: a tuple contains information about browser, context and page object

    - How to use:
        example

        _browser, _context, _page = open_new_page(
        proxy_info = {
            "server": "http://resource.com:3000", 
        },
        headless = True,
        )

        page.goto("http://test_local.com")

    '''

    p = sync_playwright().start()

    browser, context, page = _instantiate_browser_context_page(
        p,
        proxy_info=proxy_info,
        headless=headless,
        accept_downloads=accept_downloads,
        block_resources=block_resources,
        cookies=cookies,
    )

    return browser, context, page


def with_page(**kwargs):
    '''
    Decorator is designed to simplify the process of creating and managing a Playwright browser, context, and page within configurations.

    - Args:
        kwargs: keyword arguments for configurating the browser and page behavior

        Keyword arguments should be:
            proxy_info (dict, optional)             : proxy configuration information
                Default value: None
            headless (boo, optional)                : the checker to run browser in headless mode or not
                Default value: True
            accpet_downloads (bool, optional)       : the checker to accept downloads
                Default value: True
            block_resources (bool | list, optinal)  : Determines if and which resources to block.
                If value was True, it default blocks EXCLUDED_RESOURCES_TYPES.
                If a list is provided, it blocks the specified resource types.
                Default value: True
            ... more customization arguments

    - Return:
        callable: a decorated function that can be used for web automation with an open Playwright page.

    - How to use:
        example

        @with_page(headless=True, accept_downloads=False, block_resources=["image"])
        def automate_customize(page):
            page.goto("https://google.com")

        automate_customize(page=page)

    '''

    def decorator(func):
        def func_wrapper(*func_args, **func_kwargs):
            # by default, accept_downloads=True, headless=True, block_resources=True, no proxy, no cookies
            default = {
                "accept_downloads": True,
                "headless": True,
                "block_resources": True,
                "proxy_info": None,
            }
            for k, v in default.items():
                if k not in kwargs:
                    kwargs[k] = v

            # overwrite the decorator kwargs if the ones specified by the wrapped function
            kwargs.update(func_kwargs)

            # open browser, context and page with the conditions specified in the kwargs dictionary
            with sync_playwright() as p:
                browser, context, page = _instantiate_browser_context_page(
                    p, **kwargs)

                # add the new page to the wrapped function kwargs
                func_kwargs["page"] = page

                # execute the function with the open page
                output = func(*func_args, **func_kwargs)

                # close the page and browser
                page.close()
                browser.close()

            return output

        return func_wrapper

    return decorator


# WEB SURFING
def _get_page_arg(func_args: list, func_kwargs: dict, func_name: str) -> Page:
    '''
    Retrieve a Playwright Page object from externally function arguments and keyword arguments in external

    - Args:
        func_args(list, required)       : a list of function arguments will be passed to function
        func_kwargs(dict, required)     : a dictionary of keyword arguments will be passed to function
        func_name (str, required)       : the name of the decorator function, used for message error

    - Return:
        Page: a Playwright Page object if founded it in func_kwargs or func_args

    - Raises:
        Exception: if the Page object not be founded in func_kwargs or func_args

    - How to use:
        exmaple

        func_args, func_kwargs, func_name = [], {}, "func_name"
        page = _get_page_arg(func_args, func_kwargs, func_name)

    '''

    page = None

    # overriding page by the page value in func_kwargs and func_args
    if func_kwargs:
        page = func_kwargs.get("page")
    if (not page) and func_args:
        page = func_args[0]
    if not isinstance(page, Page):
        raise Exception(
            f"One of the decorator expects the function `{func_name}` to have a page as first arg or as kwarg."
        )
    return page


def wait_after_execution(wait_ms: int = 2000, randomized: bool = True):
    '''
    Decorator to add a wait period after executing a function in web automation.

    This decorator allows you to introduce a delay (in milliseconds) after executing a function.

    - Args:
        wait_ms (int, optional)         : the number shows the miliseconds to wait
            Default value: 2,000 ms (2 seconds)
        randomized (bool, optional)     : the checker to randomize the wait time within a 15% range (0.85,1.15) around 'wait_ms'.
            Default value: True

    - Return:
        callable: a decorator function that adds a wait period after execution.

    - How to use:
        example

        @@wait_after_execution(wait_ms=5000, randomized=False)
        def perform_action_and_wait(page):
            page.click(button="right")
            # Add any actions you want to perform after clicking
            # See more:
            # - https://playwright.dev/python/docs/api/class-page#page-click

        # Calling the decorated function will execute the action and then wait for 5 seconds:
        perform_action_and_wait(page)

    '''

    def decorator(func):
        def func_wrapper(*func_args, **func_kwargs):
            # get the page object. Check the kwargs first, then the first args
            page = _get_page_arg(func_args, func_kwargs, func.__name__)

            # execute the function
            output = func(*func_args, **func_kwargs)

            # wait for the given time before moving to the next command
            nonlocal wait_ms
            # the wait_ms value can be overwritten if it is specified as a kwarg in the wrapped function
            if func_kwargs and ("wait_ms" in func_kwargs):
                wait_ms = func_kwargs.get("wait_ms")

            if randomized:
                # take a random number in the 15% range around the input time in millisecond
                min = int(wait_ms * 0.85 + 0.5)
                max = int(wait_ms * 1.15 + 0.5)
                wait_ms = randint(min, max)
            # wait for the given time before moving to the next command
            page.wait_for_timeout(wait_ms)

            return output

        return func_wrapper

    return decorator


def check_for_loaded_marker(
    marker: str | Locator = None,
    marker_strict: bool = False,
    load_message: str = None,
    timeout: int = 10000,
):
    '''
    Decorator to check for the visibility of a marker on the web page before and after executing a function.

    This decorator allows you to ensure that a specific element or condition, represented by a marker,
    is visible on the web page before executing a function. 

    - Args:
        marker (str | Locator, optional): the marker element or condition to check. It can be specified as a CSS selector string or a Playwright Locator. 
            Defaults to None.
        marker_strict (bool, optional): the checker for the marker selector should be used strictly (with a dot prefix) when building the Locator. 
            Defaults to False.
        load_message (str, optional): a custom message to log when the marker is considered loaded.
            Defaults to None.
        timeout (int, optional): the maximum time (in milliseconds) to wait for the marker to become visible.
            Defaults to 10,000 ms (10 seconds).

    - Returns:
        callable: A decorated function that checks for the marker's visibility before and after execution.

    - How to use:
        example

        @check_for_loaded_marker(".loading-spinner", marker_strict=True, load_message="Page has loaded successfully.")
        def perform_action_after_loading(page):
            page.click(button="right")
            # See more:
            # - https://playwright.dev/python/docs/api/class-page#page-click

        perform_action_after_loading(page)

    '''

    def decorator(func):
        def func_wrapper(*func_args, **func_kwargs):
            # get the page object. Check the kwargs first, then the first args
            page = _get_page_arg(func_args, func_kwargs, func.__name__)

            # execute the function
            output = func(*func_args, **func_kwargs)

            # build the marker locator if needed
            nonlocal marker
            if isinstance(marker, str):
                # add a dot before the marker if it misses it
                if not (marker_strict) and not (marker.startswith(".")):
                    marker = "." + marker
                # make the marker a playwright Locator
                marker = page.locator(marker)
                # wait for the marker to be visible
                marker.wait_for(timeout=timeout)
                logging.debug(
                    load_message
                    if load_message
                    else "[playwright_plus] loaded marker visible."
                )

            return output

        return func_wrapper

    return decorator
