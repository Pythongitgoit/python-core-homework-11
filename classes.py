from collections import UserDict
from datetime import datetime
import re

RED = "\033[91m"
GREEN = "\033[92m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
AQUA = "\033[96m"
RESET = "\033[0m"


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
    def __init__(self, value):
        super().__init__(value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        if not new_value:
            raise ValueError("Name cannot be empty")
        if not re.match(r"^[A-Za-z]*$", new_value):
            raise ValueError(
                f"Name {RED}{new_value}{RESET} should only contain letters"
            )
        self._value = new_value


class Phone(Field):
    def __init__(self, value):
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        if len(new_value) != 10 or not new_value.isdigit():
            raise ValueError(f"Incorrect phone {RED}{new_value}{RESET} number format")
        self._value = new_value


class Birthday(Field):
    def __init__(self, value):
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        try:
            self.date = datetime.strptime(new_value, "%Y-%m-%d")
        except ValueError:
            raise ValueError(
                f"Incorrect {RED}{new_value}{RESET} format. Please use YYYY-MM-DD format"
            )
        self._value = new_value

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

            try:
                name_field = Name(name)  # Використовуємо клас Name для валідації імені
            except ValueError as e:
                print(str(e))
                return

            try:
                phone1_field = Phone(
                    phone1
                )  # Використовуємо клас Phone для валідації телефону
            except ValueError as e:
                print(str(e))
                return

            if phone2:
                try:
                    phone2_field = Phone(phone2)
                except ValueError as e:
                    print(str(e))
                    return

            try:
                record = Record(name_field.value, birthday)
            except ValueError as e:
                print(str(e))
                return

            record.add_phone(phone1_field.value)

            if phone2:
                record.add_phone(phone2_field.value)

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
