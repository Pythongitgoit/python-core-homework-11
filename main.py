from collections import UserDict
from datetime import datetime

RED = "\033[91m"
GREEN = "\033[92m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
AQUA = "\033[96m"
RESET = "\033[0m"


def user_error(func):
    def inner(*args):
        try:
            return func(*args)
        except IndexError:
            return "Not enough params."
        except KeyError:
            return "Unknown record_id."
        except ValueError:
            return "Error: Invalid value format."

    return inner


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

    def set_value(self, value):
        self.value = value

    def get_value(self):
        return self.value


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if len(value) != 10 or not value.isdigit():
            raise ValueError("Incorrect phone number format")
        super().__init__(value)

    def set_value(self, value):
        if len(value) != 10 or not value.isdigit():
            raise ValueError("Incorrect phone number format")
        super().set_value(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            self.date = datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            raise ValueError(
                f"Incorrect {RED}{value}{RESET} format. Please use YYYY-MM-DD format."
            )
        super().__init__(value)

    def set_value(self, value):
        try:
            self.date = datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Incorrect date format. Please use YYYY-MM-DD format.")
        super().set_value(value)

    def __str__(self):
        return self.value


class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
        if birthday:
            self.birthday = Birthday(birthday)

    def add_phone(self, phone):
        if len(self.phones) < 2:
            phone_item = Phone(phone)
            self.phones.append(phone_item)
        else:
            raise ValueError("A contact can have at most 2 phones")

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        if len(new_phone) != 10 or not new_phone.isdigit():
            raise ValueError(f"Incorrect phone {RED}{new_phone}{RESET} number format")

        found = False

        for phone_item in self.phones:
            if phone_item.value == old_phone:
                phone_item.value = new_phone
                found = True

        if not found:
            raise ValueError(f"The Number {RED}{old_phone}{RESET} Does Not Exist")

    def find_phone(self, phone):
        for phone_item in self.phones:
            if phone_item.value == phone:
                return phone_item
        return None

    def days_to_birthday(self):
        if self.birthday:
            today = datetime.now()
            birthdate = self.birthday.date.replace(year=today.year)
            if today > birthdate:
                birthdate = birthdate.replace(year=today.year + 1)
            delta = birthdate - today
            return delta.days
        else:
            return None

    def __str__(self):
        phone_str = "; ".join(str(p) for p in self.phones)
        birthday_str = f"Birthday: {AQUA}{self.birthday}" if self.birthday else ""
        days_to_birthday = (
            f"Days to Birth: {AQUA}{self.days_to_birthday()}" if self.birthday else ""
        )
        return f"{MAGENTA}Contact name: {AQUA}{self.name.value},{MAGENTA} phones:{AQUA} {phone_str}, {MAGENTA} {birthday_str}, {MAGENTA}{days_to_birthday}{RESET}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def show_all_contacts(self):
        for record in self.values():
            print(record)

    def add_contact(self, name, phone1, phone2=None, birthday=None):
        if name:
            if name in self.data:
                print(
                    f"A contact with the name {RED}'{name}'{RESET} already exists. Choose a different name or use 'edit'."
                )
                return

            if len(phone1) != 10 or not phone1.isdigit():
                print(
                    f"Error: Incorrect phone1 {RED} {phone1}{RESET}. Please enter a 10-digit phone number."
                )
                return
            if phone2 and (len(phone2) != 10 or not phone2.isdigit()):
                print(
                    f"Error: Incorrect phone2 {RED} {phone2}{RESET}. Please enter a 10-digit phone number."
                )
                return

            try:
                record = Record(name, birthday)
            except ValueError as e:
                print(str(e))
                return

            record.add_phone(phone1)

            if phone2:
                record.add_phone(phone2)

            self.add_record(record)
            print(f"Contact {GREEN}'{name}'{RESET} added.")
        else:
            print("Error: Invalid contact name.")

    def find_contact(self, name):
        found_record = self.find(name)
        if found_record:
            print(found_record)
        else:
            print(f"Contact{RED} '{name}'{RESET} not found.")

    def delete_contact(self, name):
        if name in self.data:
            del self.data[name]
            print(f"Contact {GREEN}'{name}'{RESET} deleted.")
        else:
            print(f"Contact{RED} '{name}'{RESET} not found.")

    def iterator(self, page_size):
        total_records = len(self.data)
        records = list(self.data.values())
        current_page = 0
        while current_page < total_records:
            yield records[current_page : current_page + page_size]
            current_page += page_size


def parse_command(command: str):
    parts = command.split()
    if len(parts) < 1:
        return None, []
    action = parts[0].lower()
    args = parts[1:]
    return action, args


@user_error
def main():
    book = AddressBook()

    while True:
        user_input = input(
            f"{BLUE}Enter a command {RESET}(add/show(2)/find/edit/delete/exit(6)): "
        ).strip()

        if user_input == "exit" or user_input == "6":
            print(f"\u001b[0m\u001b[7m Goodbye! \u001b[0m")
            break

        action, args = parse_command(user_input)

        if action == "add":
            if len(args) >= 2:
                name = args[0]
                phone1 = args[1]
                phone2 = args[2] if len(args) > 2 else None
                birthday = args[3] if len(args) > 3 else None

                book.add_contact(name, phone1, phone2, birthday)
            else:
                print(f"Invalid arguments for {RED}'add'{RESET} command.")

        elif action == "show" or action == "2":
            page_size = input(f"{BLUE}Enter the number of records to display: {RESET}")
            try:
                page_size = int(page_size)
                for page in book.iterator(page_size):
                    for record in page:
                        print(record)
                    show_more = input(
                        f"{BLUE}Show more? Press(2) to continue or Press any key to return to the main menu:{RESET} "
                    )
                    if show_more.lower() != "2":
                        break
            except ValueError:
                print(f"{RED}Invalid number. Please enter a valid number.{RESET}")

        elif action == "edit":
            if len(args) == 3:
                name = args[0]
                old_phone = args[1]
                new_phone = args[2]

                record = book.find(name)

                if record:
                    try:
                        record.edit_phone(old_phone, new_phone)
                        print(
                            f"Phone number for {GREEN}'{name}'{RESET} edited successfully."
                        )
                    except ValueError as e:
                        print(str(e))
                else:
                    print(f"Contact {RED}'{name}'{RESET} not found.")
            else:
                print(f"{RED}Invalid arguments for 'edit' command.{RESET}")

        elif action == "find":
            if len(args) == 1:
                name = args[0]
                book.find_contact(name)
            else:
                print(f"{RED}Invalid arguments for 'find' command.{RESET}")

        elif action == "delete":
            if len(args) == 1:
                name = args[0]
                book.delete_contact(name)
            else:
                print(f"{RED}Invalid arguments for 'delete' command.{RESET}")

        else:
            print(f"{RED}Unknown command. Try again.{RESET}")


if __name__ == "__main__":
    main()
