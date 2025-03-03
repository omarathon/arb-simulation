import os

class ArbEngineConfig:
    TOTAL_STAKE_PER_ARB = float(os.getenv("TOTAL_STAKE_PER_ARB", 100))

arb_engine_config = ArbEngineConfig()



