from playwright._impl._api_types import TimeoutError as PlaywrightTimeoutError


def catch_TimeoutError(
    exception_class: Exception = Exception,
    message: str = None,
):
    '''
    Decorator to catch PlaywrightTimeoutError and raise the customized exception

    This decorator can be applied the function that help to raise PlaywrightTimeoutError

    - Args:
        exception_class(Exception, optional)    : the custom exception class to raise
            Default value: Exception
        message (str, optional)                 : A custom error message to raise when the exception raised.
            Default value: None

    - Return:
        callable    : A decorated function that catches PlaywrightTimeoutError

    - How to use:
        example:

        @catch_TimeoutError(exception_class = CustomTimeoutErrorException, message="this is a example custom_time_out_error")
        def custome_func():
            pass

    '''
    def decorator(func):
        def func_wrapper(*args, **kwargs):
            try:
                output = func(*args, **kwargs)
                return output

            except PlaywrightTimeoutError as te:
                # instantiate the exception to raise.
                exception = exception_class(message)
                # customize the error message
                exception.message = f"[{func.__name__}] {exception.message}:\n{str(te)}"
                # raise the exception
                raise exception

        return func_wrapper

    return decorator
