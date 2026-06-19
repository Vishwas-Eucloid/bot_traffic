import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import testing_sb.batch_signup_ratelimit as m

m.TOTAL_ACCOUNTS = 5

m.run()
