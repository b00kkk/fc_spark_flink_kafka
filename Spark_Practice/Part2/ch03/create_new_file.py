if __name__ == '__main__':
    stocks_file_path = "data/stocks/"
    for i in range(10):
        file_name = f"{stocks_file_path}/{i}.csv"
        with open(file_name, "w") as file:
            data = "AAPL,2022.4.27,158.8278715"
            file.write(data)