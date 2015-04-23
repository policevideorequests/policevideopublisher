import traceback
import sys

class ProcessExceptionMiddleware(object):
    def process_exception(self, request, exception):
        # Just print the exception object to stdout
        print exception

        # Print the familiar Python-style traceback to stderr
        traceback.print_exc()

        # Write the traceback to a file or similar
        #myfile.write(''.join(traceback.format_exception(*sys.exc_info())))