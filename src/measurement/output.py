"""In this module, we can define a custom output method for various
running configurations."""

# For now, we only use print-outs (in order to make it run
# more easily in the distributed system).


class OutPut:
    """Static class handling console logs, data and so on.
    Format for outputs as of now: <special character>- <data/msg..>"""

    @staticmethod
    def log(msg):
        """Log message - begins with $"""
        print(f'$- {msg}')

    @staticmethod
    def data(key, value):
        """Data message - begins with * and follows <key>;<value> format."""
        print(f'*- {key};{value}')

    @staticmethod
    def print(msg):
        """Printed message - begins with #, will be ignored"""
        print(f'#- {msg}')

    @staticmethod
    def error(msg):
        """Error message - begins with !"""
        print(f'!- {msg}')
