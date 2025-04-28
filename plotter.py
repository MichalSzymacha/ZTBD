import pandas as pd
import matplotlib.pyplot as plt

# Wczytaj dane
delete = pd.read_csv("benchmark_delete.csv")
query = pd.read_csv("benchmark_query.csv")
insert = pd.read_csv("benchmark_insert.csv")
insert_time = pd.read_csv("insert_time.csv")


# Funkcja do tworzenia wykresów benchmarków
def plot_benchmark(data, title, filename):
    plt.figure(figsize=(10, 6))
    colors = plt.get_cmap("tab10").colors  # Użyj palety 'tab10'
    for idx, operation in enumerate(data["Operation"].unique()):
        subset = data[data["Operation"] == operation]
        plt.plot(
            subset["Test size"],
            subset["Time (seconds)"],
            marker="o",
            label=operation,
            color=colors[idx % len(colors)],
        )
    plt.title(title)
    plt.xlabel("Wielkość testu (ilość rekordów)")
    plt.ylabel("Czas (sekundy)")
    # plt.xticks(sorted(data["Test size"]), rotation=45)  # Ustaw tylko istniejące punkty
    plt.ticklabel_format(style="plain", axis="x")  # Normalny zapis liczb
    plt.legend()
    plt.grid(True)
    plt.savefig(filename)
    plt.close()


# Tworzenie wykresów dla DELETE, GROUP BY i INSERT
plot_benchmark(delete, "Czas operacji DELETE", "delete_plot.png")
plot_benchmark(query, "Czas operacji GROUP BY", "query_plot.png")
plot_benchmark(insert, "Czas operacji INSERT", "insert_plot.png")

# Specjalny wykres dla porównania INSERT w różnych bazach danych
plt.figure(figsize=(10, 6))
colors = plt.get_cmap("tab10").colors  # Użyj palety 'tab10'
for idx, db in enumerate(insert_time["Operation"].unique()):
    subset = insert_time[insert_time["Operation"] == db]
    plt.plot(
        subset["Test size"],
        subset["Time (seconds)"],
        marker="o",
        label=db,
        color=colors[idx % len(colors)],
    )
plt.title("Porównanie czasu operacji INSERT między bazami danych")
plt.xlabel("Wielkość testu (ilość rekordów)")
plt.ylabel("Czas (sekundy)")
# plt.xticks(sorted(insert_time["Test size"]), rotation=45)
plt.ticklabel_format(style="plain", axis="x")
plt.legend()
plt.grid(True)
plt.savefig("insert_time_comparison.png")
plt.close()

print("Wszystkie wykresy zostały zapisane!")
