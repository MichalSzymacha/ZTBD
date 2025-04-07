# main.py
import importlib


def run_module(module_name, func_name, data_size=None):
    module = importlib.import_module(f"python_scripts.{module_name}")
    func = getattr(module, func_name)
    if data_size is not None:
        func(data_size)
    else:
        func()


def main():
    data_sizes = [1000, 5000]

    print("Uruchamiamy testy MySQL...")
    for size in data_sizes:
        run_module("mysql.insert", "mysql_insert", size)
        run_module("mysql.select", "mysql_select")
        run_module("mysql.update", "mysql_update")
        run_module("mysql.delete", "mysql_delete")

    print("\nUruchamiamy testy PostgreSQL...")
    for size in data_sizes:
        run_module("postgres.insert", "pg_insert", size)
        run_module("postgres.select", "pg_select")
        run_module("postgres.update", "pg_update")
        run_module("postgres.delete", "pg_delete")

    print("\nUruchamiamy testy Cassandry...")
    for size in data_sizes:
        run_module("cassandra.initialize", "initialize_cassandra")
        run_module("cassandra.insert", "cassandra_insert", size)
        run_module("cassandra.select", "cassandra_select")
        run_module("cassandra.update", "cassandra_update")
        run_module("cassandra.delete", "cassandra_delete")

    print("\nUruchamiamy testy MongoDB...")
    for size in data_sizes:
        run_module("mongo.insert", "mongo_insert", size)
        run_module("mongo.select", "mongo_select")
        run_module("mongo.update", "mongo_update")
        run_module("mongo.delete", "mongo_delete")


if __name__ == "__main__":
    main()
