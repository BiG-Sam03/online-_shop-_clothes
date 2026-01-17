"""Online Clothes Shop System (console)

Implemented use cases:
- Register
- Login

No frameworks. No database. Local JSON file storage.
"""

import getpass

from user_repository import UserRepository


def menu() -> None:
    repo = UserRepository("users.json")

    while True:
        print("\n=== Online Clothes Shop System ===")
        print("1) Register")
        print("2) Login")
        print("3) Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            username = input("Username: ").strip()
            email = input("Email: ").strip()
            password = getpass.getpass("Password: ").strip()

            ok, msg = repo.register(username=username, email=email, password=password)
            print(msg)

        elif choice == "2":
            username = input("Username: ").strip()
            password = getpass.getpass("Password: ").strip()

            ok, msg = repo.login(username=username, password=password)
            print(msg)

        elif choice == "3":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    menu()
