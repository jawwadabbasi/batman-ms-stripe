# Include all global variables in this file.
# These are used across different modules/packages
# where required.

# Service Name
SVC_NAME = 'batman-ms-stripe'

# DB Settings
DB_HOST_WRITER = '127.0.0.1'
DB_HOST_READER = '127.0.0.1'
DB_PORT = 3306
DB_NAME = 'batman_stripe'
DB_USER = 'root'
DB_PASS = ''

# Stripe Settings
STRIPE_API_KEY = 'bt_test_'
STRIPE_PUBLIC_KEY = 'pk_test_'
WEBHOOK_SECRET_KEY = 'whsec_'

# Sentry Settings
SENTRY_DSN = ''
SENTRY_TRACES_SAMPLE_RATE = 1.0
SENTRY_PROFILES_SAMPLE_RATE = 1.0
SENTRY_ENV = 'development'

# Flask Settings
FLASK_PORT = 80
FLASK_DEBUG = True