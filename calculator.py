def simple_calculator():
    print("=== Kalkulator i thjeshte ===")
    print("Zgjidhni nje operacion:")
    print("Shkruan 'quit' per te dal nga kalkulatori.")

    while True:
        expression = input("Shkruani nje shprehje (p.sh., 2 + 3): ")

        if expression == 'quit':
            print("Duke dal nga kalkulatori. Faleminderit!")
            break

        try:
            result = eval(expression)
            print(f"Rezultati: {result}")
        except:
            print("Gabim: Shprehje e pavlefshme.")

            if __name__ == "__main__":
                simple_calculator()
                