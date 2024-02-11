from dataclasses import dataclass


@dataclass
class PhoneBook:
    """
    Класс представляющий телефонную книгу
    """

    phone_personal: str
    last_name: str = ''
    first_name: str = ''
    surname: str = ''
    organisation_name: str = ''
    phone_work: str = ''

