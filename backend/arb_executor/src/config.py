import os

class ArbExecutorConfig:
    DELAY_SECONDS_TO_EXECUTE_ARB = float(os.getenv("DELAY_SECONDS_TO_EXECUTE_ARB", 3.0))

arb_executor_config = ArbExecutorConfig()