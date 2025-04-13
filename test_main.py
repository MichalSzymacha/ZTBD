from insert_data import main
from test import run_all

def write_to_csv(filename, line):
    with open(filename, 'a') as file:
        file.write(line + '\n')
        
TEST_DATA_SIZES = [1000, 10000, 50000, 100000, 500000, 1000000, 5000000, 10000000]

for size in TEST_DATA_SIZES:
    write_to_csv('benchmark_results.csv', f"Test size: {size}")
    write_to_csv('insert_time.csv', f"Test size: {size}")
    main(size)
    run_all(int(size*0.1))