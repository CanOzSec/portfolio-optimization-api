from db import Database, StockDbOperations


def main():
	db = Database()
	db.migrate()
	StockDbOperations().prepare_stocks()


if __name__ == "__main__":
	main()