import pickle
from collections import UserDict
from datetime import datetime, date, timedelta
from colorama import Fore

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:        
            print(f"{Fore.RED}{e}{Fore.RESET}")
        except KeyError:
            print(f"{Fore.RED}Given username was not found in the contact list.{Fore.RESET}")
        except IndexError:
            print(f"{Fore.RED}Too few arguments were given.{Fore.RESET} Use '{Fore.GREEN}help{Fore.RESET}' for additional info.")
        except EmptyDictError:
            print(f"{Fore.RED} Address book is empty.{Fore.RESET} Add a contact with '{Fore.GREEN}add{Fore.RESET}' command.")
        except (PhoneAlreadyExistsError, BirthdayAlreadyExistsError, BirthdayNotSetError) as e:
            print(e)
    return inner

class ArgumentInstanceError(Exception):
    pass

class EmptyDictError(Exception):
    pass

class PhoneAlreadyExistsError(Exception):
    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(name)
    
    def __str__(self) -> str:
        return f"{Fore.RED}Given phone number is already in {Fore.RESET}{str(self.name).capitalize()}'s{Fore.RED} record.{Fore.RESET}"

class BirthdayAlreadyExistsError(Exception):
    def __init__(self, name: str) -> None:
        self.name = name.casefold().capitalize()
        super().__init__(name)
    
    def __str__(self) -> str:
        return f"{Fore.RED}{self.name}'s birthday is already set.{Fore.RESET} Use '{Fore.GREEN}change-birthday{Fore.RESET}' to edit the date."

class BirthdayNotSetError(Exception):
    def __init__(self, name: str) -> None:
        self.name = name.casefold().capitalize()
        super().__init__(name)
    
    def __str__(self) -> str:
        return f"{Fore.RED}{str(self.name).capitalize()} does not have a birthday date set.{Fore.RESET} Use '{Fore.GREEN}add-birthday{Fore.RESET}' to add the date."

class Field:
    def __init__(self, value: str) -> None:
        self.value = value

    def __str__(self) -> str:
        return self.value

class Name(Field):
    def __init__(self, name: str) -> None:
        if not name.isalpha():
            raise ValueError("Name must be alphabetic")
        super().__init__(name.casefold())

    def __eq__(self, other) -> bool:
        return isinstance(other, Name) and self.value == other.value

    def __str__(self) -> str:
        return self.value

class Phone(Field):
    def __init__(self, phone) -> None:
        if not phone.isdigit():
            raise ValueError("Phone number must consist of digits.")
        elif len(phone)!=10: 
            raise ValueError("Phone number must consist of 10 digits.")
        else:
            super().__init__(phone)

    def __eq__(self, other) -> bool:
        if isinstance(other, Phone) and self.value == other.value:
            return True
        return NotImplemented

    def __str__(self) -> str:
        return self.value

class Birthday(Field):
    def __init__(self, value):
        try:
            self.birthday = datetime.strptime(value, "%d.%m.%Y")
            super().__init__(value)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
    
    def __str__(self):
        return self.value

class Record:
    def __init__(self, name: str) -> None:
        self.name = Name(name)
        self.phones = []
        self.birthday = None
    
    def add_birthday(self, birthday: str) -> None:
        self.birthday = Birthday(birthday)
    
    def change_birthday(self, birthday: str) -> None:
        self.birthday = Birthday(birthday)
        print(f"{Fore.GREEN}Birthday date updated.{Fore.RESET}")

    def add_phone(self, phone: str) -> None:
        if self.find_phone(phone):
            raise PhoneAlreadyExistsError(self.name)
        phone_obj = Phone(phone)
        self.phones.append(phone_obj)  

    def remove_phone(self, phone: str) -> None:
        phone_obj = self.find_phone(phone)
        if phone_obj:
            self.phones.remove(phone_obj)
        else:
            raise ValueError("Phone number not found.")

    def edit_phone(self, old_phone: str, new_phone: str) -> None:
        old_phone_obj = self.find_phone(old_phone)
        if old_phone_obj:
            self.phones.remove(old_phone_obj)
            new_phone_obj = Phone(new_phone)
            self.phones.append(new_phone_obj)
        else: 
            raise ValueError("Phone number not found.")

    def find_phone(self, phone: str) -> Phone | None:
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def __str__(self) -> str:
        if self.phones:
            return f"Contact name: {str(self.name).capitalize()}, phones: {'; '.join(p.value for p in self.phones)}"
        return f"There are no phones in {str(self.name).capitalize()}'s record"

class AddressBook(UserDict):
    def add_record(self, record: Record) -> None:
        if not isinstance(record, Record):
            raise ArgumentInstanceError("The argument must be a record")
        elif str(record.name) in self.data.keys():
            raise ValueError(f"Name is already in address book")
        self.data[str(record.name)] = record

    #find record by name
    def find(self, name: str) -> Record | str:
        try:
            return self.data[name.casefold()]                   
        except KeyError:
            return None

    def delete(self, name: str) -> None:
        try:
            self.data.pop(name.casefold())
        except KeyError:
            return None
    
    def __str__(self) -> str:
        result = ""
        for name, record in self.data.items():
            result += str(record) + "\n"
        return result.strip()

def parse_input(user_input: str) -> tuple[str, list[str]]:
    cmd, *args = user_input.split(" ")    
    return cmd, args

@input_error
def add_contact(args: list[str], book: AddressBook) -> str:
    if len(args) < 2:
        raise IndexError

    name, phone, *_ = args
    record = book.find(name)

    if not record:
        record_entry = Record(name)
        record_entry.add_phone(phone)
        book.add_record(record_entry)
        print(f"{Fore.GREEN}Contact added.{Fore.RESET}")
    else: 
        record.add_phone(phone)
        print(f"{Fore.GREEN}Contact updated.{Fore.RESET}")

@input_error
def change_contact(args: list[str], book: AddressBook) -> str:
    if len(args) < 3:
        raise IndexError
    
    name, old_phone, new_phone, *_ = args
    record = book.find(name)

    if record == None:
        raise KeyError
    record.edit_phone(old_phone, new_phone)
    print(f"{Fore.GREEN}Contact updated.{Fore.RESET}")

@input_error
def show_phone(args: list[str], book: AddressBook) -> str:
    if len(args) < 1:
        raise IndexError
    
    name, *_ = args
    record = book.find(name)
    if record == None:
        raise KeyError
    print(record)

@input_error
def show_all(book: AddressBook) -> str:
    if not book:
        raise EmptyDictError
    print(book)

@input_error
def add_birthday(args, book: AddressBook) -> None:
    if len(args) < 2:
        raise IndexError
    
    name, birthday, *_ = args
    record = book.find(name)
    if not record:
        raise ValueError(f"Record with name '{name}' was not found.")
    elif record.birthday == None:
        record.add_birthday(birthday)
        print(f"{Fore.GREEN}Birthday added to {name.casefold().capitalize()}'s record.{Fore.RESET}")
    else:
        raise BirthdayAlreadyExistsError(str(name))

@input_error
def change_birthday(args, book: AddressBook) -> None:
    if len(args) < 2:
        raise IndexError
    
    name, birthday, *_ = args
    record = book.find(name)
    if not record:
        raise ValueError(f"Record with name '{name}' was not found.")
    record.change_birthday(birthday)
    
@input_error
def show_birthday(args, book: AddressBook) -> Birthday:
    if len(args) < 1:
        raise IndexError
    
    name, *_ = args
    record = book.find(name)
    if record == None:
        raise KeyError
    elif record.birthday == None:
        raise BirthdayNotSetError(name)
    else: 
        print(f"{name.casefold().capitalize()}'s birthday is on {Fore.GREEN}{record.birthday}{Fore.RESET}")

@input_error
def birthdays(book: AddressBook):
    if not book:
        raise EmptyDictError
    
    upcoming_birthdays = get_upcoming_birthdays(book)
    heading_message = f"{Fore.YELLOW}Upcoming birthdays in your address book:{Fore.RESET}"
    birthdays_list = [f"\n - {item[0]}: {item[1]}" for birthday in upcoming_birthdays for item in birthday.items()]
    final_list = [heading_message] + birthdays_list
    print("".join(final_list))

def get_upcoming_birthdays(book: AddressBook) -> list:
    congratulate_users = []
    today = date.today()
    for name, record in book.items():
        if not record.birthday:
            continue
        birthday = datetime.strptime(str(record.birthday), r"%d.%m.%Y").date()
        birthday_this_year = date(today.year, birthday.month, birthday.day)
        if birthday_this_year - today <= timedelta(days=7):         #check whether it's in the upcoming week 
            if birthday_this_year < today:                          #check if it's already too late. then +1 year = "Якщо так, розгляньте дату на наступний рік"
                birthday_this_year = date(birthday_this_year.year + 1, birthday.month, birthday.day)
            #check for weekends
            if birthday_this_year.weekday() == 5:
                birthday_this_year = birthday_this_year + timedelta(days=2)
            elif birthday_this_year.weekday() == 6:
                birthday_this_year = birthday_this_year + timedelta(days=1)

            birthday_this_year = birthday_this_year.strftime(r"%d.%m.%Y")
            congratulate_users.append({name: birthday_this_year})
    return congratulate_users

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()
    
def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

if __name__ == "__main__":
    book = load_data()
    # book = load_data("abcd.pkl")
    print(f"{Fore.YELLOW}Welcome to the assistant bot!{Fore.RESET}")
    try:
        while True:
            user_input = input("Enter a command: ").strip().casefold()
            if len(user_input) < 1:
                print(f"{Fore.RED}Too few arguments were given.{Fore.RESET} Use '{Fore.GREEN}help{Fore.RESET}' for additional info.")
                continue
            
            command, args = parse_input(user_input)

            match command:
                case "hello":
                    print(f"{Fore.YELLOW}How can I help you?{Fore.RESET}")
                case "add":
                    add_contact(args, book)
                case "change":
                    change_contact(args, book)
                case "phone":
                    show_phone(args, book)
                case "all":
                    show_all(book)
                case "add-birthday":
                    add_birthday(args, book)
                case "change-birthday":
                    change_birthday(args, book)
                case "show-birthday":
                    show_birthday(args, book)
                case "birthdays":
                    birthdays(book)
                case "close" | "exit":
                    save_data(book)
                    # save_data(book, "abcd.pkl")
                    print(f"{Fore.YELLOW}Goodbye!{Fore.RESET}")
                    break
                case "help":
                    print(f"""
The following commands are available:
    * {Fore.GREEN + 'add [username] [phone_number]':<60}{Fore.RESET} - add a contact to the contact list. note: phone number must consist of 10 digits
    * {Fore.GREEN + 'change [username] [old_phone_number] [new_phone_number]':<60}{Fore.RESET} - change an already existing contact
    * {Fore.GREEN + 'phone [username]':<60}{Fore.RESET} - get to know a phone number by the contact's username
    * {Fore.GREEN + 'add-birthday [username] [birthday]':<60}{Fore.RESET} - set a birthday date for a contact
    * {Fore.GREEN + 'change-birthday [username] [new_birthday]':<60}{Fore.RESET} - change birthday date for a contact
    * {Fore.GREEN + 'show-birthday [username]':<60}{Fore.RESET} - get to know the birthday date of the contact
    * {Fore.GREEN + 'birthdays':<60}{Fore.RESET} - get to know birthdays from your address book for upcoming week
    * {Fore.GREEN + 'all':<60}{Fore.RESET} - get all contacts from the contact list
    * {Fore.GREEN + 'exit':<60}{Fore.RESET} - close the program
    * {Fore.GREEN + 'close':<60}{Fore.RESET} - close the program""")
                case _:
                    print(f"{Fore.RED}Unknown command was given.{Fore.RESET} Use '{Fore.GREEN}help{Fore.RESET}' for additional info.")
    except KeyboardInterrupt:
        save_data(book)
        # save_data(book, "abcd.pkl")
