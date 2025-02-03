import settings

from includes.db import Db

class Schema:

	def CreateDatabase():

		return Db.ExecuteQuery(f"CREATE DATABASE IF NOT EXISTS {settings.DB_NAME} CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci",None,True,True)

	def CreateTables():

		#####################################################################################################
		query = """
			CREATE TABLE IF NOT EXISTS customers (
				customer_id VARCHAR(45) PRIMARY KEY NOT NULL,
				user_id VARCHAR(45) NOT NULL,
				email VARCHAR(150) NOT NULL,
				phone VARCHAR(15) NOT NULL, 
				disabled TINYINT DEFAULT 0,
				date DATETIME NOT NULL
			) ENGINE=INNODB;
		"""

		if not Db.ExecuteQuery(query,None,True):
			return False

		Db.ExecuteQuery("ALTER TABLE customers ADD INDEX customer_id (customer_id);",None,True)
		Db.ExecuteQuery("ALTER TABLE customers ADD INDEX user_id (user_id);",None,True)
		Db.ExecuteQuery("ALTER TABLE customers ADD INDEX email (email);",None,True)
		Db.ExecuteQuery("ALTER TABLE customers ADD INDEX phone (phone);",None,True)
		Db.ExecuteQuery("ALTER TABLE customers ADD INDEX disabled (disabled);",None,True)
		Db.ExecuteQuery("ALTER TABLE customers ADD INDEX date (date);",None,True)
		#####################################################################################################

		#####################################################################################################
		query = """
			CREATE TABLE IF NOT EXISTS invoices (
				invoice_id VARCHAR(45) PRIMARY KEY NOT NULL,
				receipt_id VARCHAR(45) NOT NULL,
				user_id VARCHAR(45) NOT NULL,
				customer_id VARCHAR(45) NOT NULL,
				subscription_id VARCHAR(45) NOT NULL,
				plan_id VARCHAR(45) NOT NULL,
				product_id VARCHAR(45) NOT NULL,
				event_type VARCHAR(50) NOT NULL,
				description TEXT NOT NULL,
				currency VARCHAR(3) NOT NULL,
				billing_interval VARCHAR(10) NOT NULL,
				amount DECIMAL(10, 2) NOT NULL,
				amount_paid DECIMAL(10, 2) NOT NULL,
				status VARCHAR(50) NOT NULL,
				invoice_data JSON NOT NULL,
				period_start DATETIME,
				period_end DATETIME,
				date DATETIME NOT NULL
			) ENGINE=INNODB;
		"""

		if not Db.ExecuteQuery(query,None,True):
			return False

		Db.ExecuteQuery("ALTER TABLE invoices ADD INDEX invoice_id (invoice_id);",None,True)
		Db.ExecuteQuery("ALTER TABLE invoices ADD INDEX receipt_id (receipt_id);",None,True)
		Db.ExecuteQuery("ALTER TABLE invoices ADD INDEX user_id (user_id);",None,True)
		Db.ExecuteQuery("ALTER TABLE invoices ADD INDEX customer_id (customer_id);",None,True)
		Db.ExecuteQuery("ALTER TABLE invoices ADD INDEX subscription_id (subscription_id);",None,True)
		Db.ExecuteQuery("ALTER TABLE invoices ADD INDEX plan_id (plan_id);",None,True)
		Db.ExecuteQuery("ALTER TABLE invoices ADD INDEX product_id (product_id);",None,True)
		Db.ExecuteQuery("ALTER TABLE invoices ADD INDEX event_type (event_type);",None,True)
		Db.ExecuteQuery("ALTER TABLE invoices ADD INDEX description (description);",None,True)
		Db.ExecuteQuery("ALTER TABLE invoices ADD INDEX currency (currency);",None,True)
		Db.ExecuteQuery("ALTER TABLE invoices ADD INDEX billing_interval (billing_interval);",None,True)
		Db.ExecuteQuery("ALTER TABLE invoices ADD INDEX amount (amount);",None,True)
		Db.ExecuteQuery("ALTER TABLE invoices ADD INDEX status (status);",None,True)
		Db.ExecuteQuery("ALTER TABLE invoices ADD INDEX period_start (period_start);",None,True)
		Db.ExecuteQuery("ALTER TABLE invoices ADD INDEX period_end (period_end);",None,True)
		Db.ExecuteQuery("ALTER TABLE invoices ADD INDEX date (date);",None,True)
		#####################################################################################################

		#####################################################################################################
		query = """
			CREATE TABLE IF NOT EXISTS subscriptions (
				subscription_id VARCHAR(45) PRIMARY KEY NOT NULL,
				user_id VARCHAR(45) NOT NULL,
				customer_id VARCHAR(45) NOT NULL,
				plan_id VARCHAR(45) NOT NULL,
				product_id VARCHAR(45) NOT NULL,
				event_type VARCHAR(50) NOT NULL,
				billing_interval VARCHAR(10) NOT NULL,
				amount DECIMAL(10, 2) NOT NULL,
				currency VARCHAR(3) NOT NULL,
				status VARCHAR(20) NOT NULL,
				disabled TINYINT DEFAULT 0,
				subscription_data JSON NOT NULL,
				period_start DATETIME,
				period_end DATETIME,
				last_updated DATETIME,
				date DATETIME NOT NULL
			) ENGINE=INNODB;
		"""

		if not Db.ExecuteQuery(query,None,True):
			return False

		Db.ExecuteQuery("ALTER TABLE subscriptions ADD INDEX subscription_id (subscription_id);",None,True)
		Db.ExecuteQuery("ALTER TABLE subscriptions ADD INDEX user_id (user_id);",None,True)
		Db.ExecuteQuery("ALTER TABLE subscriptions ADD INDEX customer_id (customer_id);",None,True)
		Db.ExecuteQuery("ALTER TABLE subscriptions ADD INDEX plan_id (plan_id);",None,True)
		Db.ExecuteQuery("ALTER TABLE subscriptions ADD INDEX product_id (product_id);",None,True)
		Db.ExecuteQuery("ALTER TABLE subscriptions ADD INDEX event_type (event_type);",None,True)
		Db.ExecuteQuery("ALTER TABLE subscriptions ADD INDEX billing_interval (billing_interval);",None,True)
		Db.ExecuteQuery("ALTER TABLE subscriptions ADD INDEX amount (amount);",None,True)
		Db.ExecuteQuery("ALTER TABLE subscriptions ADD INDEX currency (currency);",None,True)
		Db.ExecuteQuery("ALTER TABLE subscriptions ADD INDEX status (status);",None,True)
		Db.ExecuteQuery("ALTER TABLE subscriptions ADD INDEX disabled (disabled);",None,True)
		Db.ExecuteQuery("ALTER TABLE subscriptions ADD INDEX period_start (period_start);",None,True)
		Db.ExecuteQuery("ALTER TABLE subscriptions ADD INDEX period_end (period_end);",None,True)
		Db.ExecuteQuery("ALTER TABLE subscriptions ADD INDEX last_updated (last_updated);",None,True)
		Db.ExecuteQuery("ALTER TABLE subscriptions ADD INDEX date (date);",None,True)
		#####################################################################################################

		return True