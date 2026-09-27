from logger import log_info, log_error

log_info("Jarvis started.")

try:
    x = 10 / 0
except Exception as e:
    log_error("Math Test", e)

print("Finished.")