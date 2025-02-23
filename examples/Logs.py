from requestcord import Logger

# Initialize logger with different configurations
debug_logger = Logger(level='DEBUG')
prod_logger = Logger(level='INF')
custom_logger = Logger(
    level='SUC',
    log_format="| {level:^5} | {message}"
)

# Example 1: Basic logging with default INFO level
logger = Logger()
logger.debug("This won't show in default INF level")  # Hidden
logger.info("System initialized")
logger.success("Connected to database")
logger.error("Failed to load module")

# Example 2: Debug-level logging
debug_logger.debug("Starting initialization sequence")
debug_logger.info("Loaded 142 config items")
debug_logger.success("Cache warmed up")
debug_logger.error("Missing dependency: requests")

# Example 3: User input handling
username = logger.input("Enter username")
debug_logger.debug(f"User entered: {username}")

# Example 4: Custom formatted logger
custom_logger.info("This won't show with SUC level")
custom_logger.success("Payment processed!")
custom_logger.error("Invalid API key")

# Example 5: Error-only logging
error_logger = Logger(level='ERR')
error_logger.info("System check started")  # Hidden
error_logger.success("Backup completed")  # Hidden
error_logger.error("Critical: Disk full")