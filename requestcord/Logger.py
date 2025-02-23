from requestcord import *

class Logger:
    LOG_LEVELS = {
        'DEBUG': 1,
        'INF': 2,
        'SUC': 3,
        'INP': 4,
        'ERR': 5
    }

    def __init__(self, level='INF', log_format=None):
        self.level = level
        self.log_format = log_format or "[ {timestamp} ] - {level} - {message}"
        self.log_colors = {
            'SUC': Fore.GREEN,
            'ERR': Fore.RED,
            'INF': Fore.CYAN,
            'DEBUG': Fore.YELLOW,
            'INP': Fore.BLUE
        }

    def _log(self, level, message):
        if self.LOG_LEVELS[level] >= self.LOG_LEVELS[self.level]:
            timestamp = datetime.now().strftime('%H:%M:%S')
            color = self.log_colors.get(level, Fore.WHITE)
            
            formatted = self.log_format.format(
                timestamp=f"{Fore.LIGHTBLACK_EX}{timestamp}{Style.RESET_ALL}",
                level=f"{color}[{level}]{Style.RESET_ALL}",
                message=message
            )
            
            print(formatted)

    def success(self, message):
        self._log('SUC', message)

    def error(self, message):
        self._log('ERR', message)

    def info(self, message):
        self._log('INF', message)

    def debug(self, message):
        self._log('DEBUG', message)

    def input(self, prompt):
        timestamp = datetime.now().strftime(' %H:%M:%S ')
        return input(f"[{Fore.LIGHTBLACK_EX}{timestamp}{Style.RESET_ALL}] - {Fore.BLUE}[INP]{Style.RESET_ALL} - {prompt} ")
