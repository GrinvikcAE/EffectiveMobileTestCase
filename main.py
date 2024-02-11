import re
import sys
import os
from time import sleep
from typing import List
# from pprint import pprint
import json

from phone_book import PhoneBook


TIME_SLEEP = 0.8


def clear():
    """
    Очистка терминала
    :return: None
    """

    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')


def save_book(path_to: str, lst_phones: List[PhoneBook]):
    """
    Сохранение текущей телефонной книги
    :param path_to: название файла, в который сохранится информация
    :param lst_phones: список объектов телефонной книги
    :return: None
    """

    save_to = {}
    for phone in lst_phones:
        dict_phone = phone.__dict__
        save_to[dict_phone.get('phone_personal')] = {'last_name': dict_phone.get('last_name'),
                                                     'first_name': dict_phone.get('first_name'),
                                                     'surname': dict_phone.get('surname'),
                                                     'organisation_name': dict_phone.get('organisation_name'),
                                                     'phone_work': dict_phone.get('phone_work')}
    if path_to == '':
        path_to = 'save_book'
    with open(f'saves/{path_to}.json', 'w', encoding='utf8') as save_file:
        json.dump(save_to, save_file, indent=3, ensure_ascii=False)


def load_book(path_to_file: str) -> List[PhoneBook]:
    """
    Загрузка телефонной книги
    :param path_to_file: название файла, который будет загружен; в случае пустого названия будет попытка загрузки
    стандартного файла
    :return: список объектов телефонной книги
    """

    lst_phones = []
    if path_to_file == '':
        path_to_file = 'save_book.json'
    try:
        with open(f'saves/{path_to_file}', encoding='utf8') as file:
            dict_phone = json.load(file)
            for phone in dict_phone:
                lst_phones.append(PhoneBook(phone_personal=phone,
                                            last_name=dict_phone[phone].get('last_name'),
                                            first_name=dict_phone[phone].get('first_name'),
                                            surname=dict_phone[phone].get('surname'),
                                            organisation_name=dict_phone[phone].get('organisation_name'),
                                            phone_work=dict_phone[phone].get('phone_work')))
        return lst_phones
    except FileNotFoundError:
        print('Такого файла не существует')
        sleep(TIME_SLEEP)
        return []


def change_view_number(number: str) -> str:
    """
    Приведение телефонного номера к общепринятому виду
    :param number:
    :return: по необходимости возвращает измененный вид номера
    """

    if re.match(r'^(\+7|8)?\(?[489][0-9]{2}\)?[0-9]{3}[0-9]{2}[0-9]{2}$', number):
        if number[0] == '+':
            number = (f'{number[:2]}({number[2:5]})'
                      f'{number[5:8]}-{number[8:10]}-'
                      f'{number[10:]}')
        else:
            number = (f'{number[0]}({number[1:4]})'
                      f'{number[4:7]}-{number[7:9]}-'
                      f'{number[9:]}')
    return number


def get_all_phones(lst_phones: List[PhoneBook], main_list_phones: List[PhoneBook] | None = None) -> None:
    """
    Получение списка контактов в телефонной книге
    :param main_list_phones: список объектов телефонной книги без изменений
    :param lst_phones: список объектов телефонной книги, который может подтвергаться изменениям
    :return: None
    """

    total_len = len(lst_phones)
    x_point = 0
    y_point = 10 if total_len >= 10 else total_len
    total_page = total_len // 10 + 1
    page = 1

    if main_list_phones is None:
        main_list_phones = lst_phones[:]

    while True:
        clear()
        print(f'Текущая страница: {page} из {total_page}, всего найдено: {total_len}')
        print('{:<6}'.format('Индекс'),
              '{:^20}'.format('Фамилия'),
              '{:^20}'.format('Имя'),
              '{:^20}'.format('Отчество'),
              '{:^24}'.format('Личный (сотовый) номер'),
              '{:^20}'.format('Рабочий номер'),
              '{:^20}'.format('Название организации'),
              sep='', end='\n')
        for phone in lst_phones[x_point:y_point]:
            dict_phone = phone.__dict__
            print('{:<6}'.format(f'{main_list_phones.index(phone) + 1}.'),
                  f'{dict_phone.get("last_name"):^20}'
                  f'{dict_phone.get("first_name"):^20}'
                  f'{dict_phone.get("surname"):^20}'
                  f'{dict_phone.get("phone_personal"):^24} '
                  f'{dict_phone.get("phone_work"):^20}'
                  f'{dict_phone.get("organisation_name"):^20}')

        nav = input('Введите <, > или exit(e,q): ')
        match nav:
            case 'exit' | 'e' | 'q' | 'у' | 'й':
                break
            case '>':
                x_point = y_point if y_point != total_len else x_point
                y_point = y_point + 10 if (y_point + 10 <= total_len and y_point != total_len) else total_len
                page = page + 1 if page + 1 <= total_page else page
            case '<':
                y_point = x_point if x_point != 0 else 10 if total_len >= 10 else total_len
                x_point = x_point - 10 if x_point - 10 >= 0 else 0
                page = page - 1 if page - 1 >= 1 else page


def find_phone(lst_of_phones: List[PhoneBook]) -> None:
    """
    Поиск телефона с возможностью поиска по нескольким параметрам. Итоговый список сортируется от
    наибольшего совпадения к наименьшему. Подстроки не учитываются.
    :param lst_of_phones: список объектов телефонной книги
    :return: None
    """

    lst_to_find = []

    find_to = input('Введите через запятую с пробелом (", ") поля, '
                    'по которым Вы хотите вести поиск: ').lower().split(', ')
    if 'фамилия' in find_to:
        lst_name = input('Введите фамилию: ')
    else:
        lst_name = None
    if 'имя' in find_to:
        frst_name = input('Введите имя: ')
    else:
        frst_name = None
    if 'отчество' in find_to:
        srname = input('Введите отчество: ')
    else:
        srname = None
    if 'номер' in find_to or 'сотовый' in find_to or 'личный номер' in find_to or 'сотовый номер' in find_to:
        phn_personal = input('Введите личный (сотовый) номер: ')
        try:
            if phn_personal == '':
                print('Личный номер не может быть пустым')
            phn_personal = change_view_number(phn_personal)
        except Exception as e:
            print('Неверный ввод')
            sleep(TIME_SLEEP)
            return None
    else:
        phn_personal = None
    if 'рабочий' in find_to or 'рабочий номер' in find_to:
        phn_work = input('Введите рабочий номер: ')
    else:
        phn_work = None
    if 'имя организации' in find_to or 'организация' in find_to or 'название организации' in find_to:
        org_name = input('Введите название организации: ')
    else:
        org_name = None

    for phone in lst_of_phones:
        count = 0
        values_of_dict_phone = phone.__dict__.values()
        if lst_name in values_of_dict_phone:
            count += 1
        if frst_name in values_of_dict_phone:
            count += 1
        if srname in values_of_dict_phone:
            count += 1
        if phn_personal in values_of_dict_phone:
            count += 1
        if phn_work in values_of_dict_phone:
            count += 1
        if org_name in values_of_dict_phone:
            count += 1
        lst_to_find.append((count, phone))

    lst_to_find = sorted(lst_to_find, reverse=True, key=lambda x: x[0])
    lst_phones = [i[1] for i in list(filter(lambda x: x[0] > 0, lst_to_find))]
    get_all_phones(lst_phones=lst_phones, main_list_phones=lst_of_phones)


if __name__ == '__main__':

    lst_of_phones = []

    while True:
        print('Добро пожаловать в телефонную книгу!\nУ вас доступны следующие команды:\n'
              '1. exit|e|esc|q|quit - выход из программы\n'
              '2. save - сохранить текущую телефонную книгу\n'
              '3. load - загрузить возможные телефонные книги\n'
              '4. read - просмотреть телефонную книгу\n'
              '5. add - добавить новый контакт (поле личного (сотового) номера является обязательным)\n'
              '6. update - обновить информацию о существующем контакте\n'
              '7. find - найти контакт\n')
        command = input('Введите команду: ')
        match command:
            case 'exit' | 'e' | 'quit' | 'esc' | 'q' | 'у' | 'й':
                sys.exit()
            case 'save':
                name_of_save = input('Введите название сохранения или оставьте поле пустым: ')
                save_book(name_of_save, lst_of_phones)
                clear()
            case 'load':
                count = 1
                lst_files_json = []
                for file in os.listdir('saves'):
                    if file.endswith('.json'):
                        lst_files_json.append(file)
                        print(f'{count}. {file}')
                        count += 1
                name_of_save = input('Введите номер сохранения или оставьте поле пустым: ')
                if name_of_save != '':
                    try:
                        name_of_save = lst_files_json[int(name_of_save)-1]
                    except Exception as e:
                        print('Такого номера нет')
                        sleep(TIME_SLEEP)
                lst_of_phones = load_book(name_of_save)
                clear()
            case 'read':
                clear()
                get_all_phones(lst_phones=lst_of_phones)
            case 'add':
                lst_name = input('Введите фамилию или оставьте поле пустым: ')
                frst_name = input('Введите имя или оставьте поле пустым: ')
                srname = input('Введите отчество или оставьте поле пустым: ')
                phn_personal = input('Введите личный (сотовый) номер: ')
                phn_personal = change_view_number(phn_personal)
                phn_work = input('Введите рабочий номер или оставьте поле пустым: ')
                org_name = input('Введите название организации или оставьте поле пустым: ')
                lst_of_phones.append(PhoneBook(phone_personal=phn_personal, last_name=lst_name, first_name=frst_name,
                                               surname=srname, organisation_name=org_name, phone_work=phn_work))
                print('Запись добавлена')
            case 'update':
                print('Вы уже знаете индекс контакта, который хотите изменить? [Д/н?]')
                check = input('Введите Д (да) или н (нет): ')
                if check == 'н':
                    print('Вам нужна помощь с поиском? [Д/н?]')
                    check = input('Введите Д (да) или н (нет): ')
                    if check == 'н':
                        get_all_phones(lst_phones=lst_of_phones)
                    else:
                        find_phone(lst_of_phones)
                number_of_phone = int(input('Введите номер контакта, который Вы хотите изменить: '))
                change_from = input('Введите, что Вы хотите изменить: ').lower()
                change_to = input('Введите изменение: ')
                match change_from:
                    case 'фамилия' | 'фамилию':
                        lst_of_phones[number_of_phone - 1].last_name = change_to
                    case 'имя':
                        lst_of_phones[number_of_phone - 1].first_name = change_to
                    case 'отчество':
                        lst_of_phones[number_of_phone - 1].surname = change_to
                    case 'сотовый' | 'сотовый номер' | 'личный номер' | 'личный' | 'телефон':
                        change_to = change_view_number(change_to)
                        lst_of_phones[number_of_phone - 1].phone_personal = change_to
                    case 'рабочий номер' | 'рабочий' | 'телефон рабочий':
                        lst_of_phones[number_of_phone - 1].phone_work = change_to
                    case 'имя организации' | 'организацию' | 'организация' | 'название организации':
                        lst_of_phones[number_of_phone - 1].organisation_name = change_to
                    case _:
                        print('Таких полей нет')
                clear()
            case 'find':
                clear()
                find_phone(lst_of_phones)
                print()
            case _:
                print('Такой команды нет')
                sleep(TIME_SLEEP)
