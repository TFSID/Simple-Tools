# calculator.py
"""
A simple command-line calculator program.

This script provides basic arithmetic operations (addition, subtraction,
multiplication, and division) and handles common errors like division by zero
and invalid user input.
"""


def add(x: float, y: float) -> float:
    """
    Adds two numbers and returns their sum.

    Args:
        x (float): The first number.
        y (float): The second number.

    Returns:
        float: The sum of x and y.
    """
    return x + y


def subtract(x: float, y: float) -> float:
    """
    Subtracts the second number from the first and returns the difference.

    Args:
        x (float): The first number (minuend).
        y (float): The second number (subtrahend).

    Returns:
        float: The difference between x and y.
    """
    return x - y


def multiply(x: float, y: float) -> float:
    """
    Multiplies two numbers and returns their product.

    Args:
        x (float): The first number.
        y (float): The second number.

    Returns:
        float: The product of x and y.
    """
    return x * y


def divide(x: float, y: float) -> float:
    """
    Divides the first number by the second and returns the quotient.

    Args:
        x (float): The numerator.
        y (float): The denominator.

    Returns:
        float: The quotient of x and y.

    Raises:
        ValueError: If the denominator (y) is zero.
    """
    if y == 0:
        raise ValueError("Cannot divide by zero.")
    return x / y


def get_float_input(prompt: str) -> float:
    """
    Prompts the user for a float input and ensures valid numerical input.

    Repeatedly prompts until a valid float is entered.

    Args:
        prompt (str): The message to display to the user.

    Returns:
        float: The validated float input from the user.
    """
    while True:
        try:
            user_input = input(prompt)
            return float(user_input)
        except ValueError:
            print("Invalid input. Please enter a valid number.")


def main():
    """
    Main function to run the simple command-line calculator program.

    It presents a menu of operations, takes user input for numbers and
    operation choice, performs the calculation, and handles potential errors.
    The program continues until the user chooses to exit.
    """
    print("--------------------------------")
    print("  Simple Command-Line Calculator")
    print("--------------------------------")

    while True:
        print("\nSelect operation:")
        print("1. Add")
        print("2. Subtract")
        print("3. Multiply")
        print("4. Divide")
        print("5. Exit")

        choice = input("Enter choice (1/2/3/4/5): ")

        if choice == '5':
            print("Exiting calculator. Goodbye!")
            break

        if choice in ('1', '2', '3', '4'):
            num1 = get_float_input("Enter first number: ")
            num2 = get_float_input("Enter second number: ")

            try:
                if choice == '1':
                    result = add(num1, num2)
                    print(f"{num1} + {num2} = {result}")
                elif choice == '2':
                    result = subtract(num1, num2)
                    print(f"{num1} - {num2} = {result}")
                elif choice == '3':
                    result = multiply(num1, num2)
                    print(f"{num1} * {num2} = {result}")
                elif choice == '4':
                    result = divide(num1, num2)
                    print(f"{num1} / {num2} = {result}")
            except ValueError as e:
                # Handles specific calculation errors (e.g., division by zero)
                print(f"Error: {e}")
            except Exception as e:
                # Catches any other unexpected errors during calculation
                print(f"An unexpected error occurred: {e}")
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")


if __name__ == "__main__":
    main()