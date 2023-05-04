import argparse
import sqlite3
import os
import logging
from typing import Union
from enum import Enum

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig(format='[%(asctime)s]: %(levelname)s'
                    ' - %(message)s')

# TODO: update someone's number is left - done
# what if someone have two numbers - done
# while creating a new value what if it's already present - done
# while retreiving data what if the contact is not present - done => ask MD
# during deletion what if the contact is not present - done
# arguments handling quality should be increased - nothing to do
# unit tests need to be written
# type check of arguments - not needed as we are already converting
# add logging functionalities - done
# handle keyboard interrupt in inputting Y/N - done
# if there are two numbers, ask which one to delete - done
# during deletion tell if that contact doesn't exist if is so - done
# during update if two numbers are present ask which one to update - done

FILE_PATH = os.path.abspath(__file__)
PROJ_DIR = os.path.dirname(FILE_PATH)
DB_FILE = os.path.join(PROJ_DIR, 'test.db')


class CommandTypes(str, Enum):

    CHECK = "check"
    EXECUTE = "Execute"
    CREATE = "CreateTable"


def sql_execute(cmd: str, mode: str, *args) -> Union[bool, list]:
    try:
        conn = sqlite3.connect(DB_FILE)
        if CommandTypes.CHECK == mode or CommandTypes.CREATE == mode:
            cursor = conn.cursor()
            cursor.execute(cmd)
            result = cursor.fetchone()
            if result:
                return True
            else:
                return False
        elif CommandTypes.EXECUTE == mode:
            response = conn.execute(cmd, args)
            conn.commit()
            return list(response)
        else:
            logger.error("Not a valid mode")
            return False
    except sqlite3.Error as e:
        logger.info(f"Error occured in sql query : {e}")
        return False
    finally:
        try:
            conn.close()
        except NameError:
            pass


def update_value_db(name: str, phone: int) -> None:
    rows = sql_execute("SELECT * FROM PHONEBOOK", CommandTypes.EXECUTE)
    updated = False
    for _name, _phone in rows:
        if _name == name:
            while True:
                choice = input(
                    "Do you want to update this number"
                    f"Y/N? : {_phone} : ")
                if choice.upper() == 'Y':
                    sql_execute(
                        "UPDATE PHONEBOOK set PHONE = (?) where PHONE = (?)",
                        CommandTypes.EXECUTE, phone, _phone)
                    updated = True
                    logger.info("Contact updated")
                    break
                elif choice.upper() == 'N':
                    break
            if updated:
                break
    else:
        logger.info("This contact is not present in phone book")
        logger.info("Exiting")


def delete_from_db(name: str) -> None:
    rows = sql_execute("SELECT * FROM PHONEBOOK", CommandTypes.EXECUTE)
    presence = False
    for _name, _phone in rows:
        if _name == name:
            presence = True
            while True:
                choice = input(
                    "Do you want to delete this number"
                    f"Y/N? : {_phone} : ")
                if choice.upper() == 'Y':
                    sql_execute(
                        "DELETE FROM PHONEBOOK WHERE PHONE=(?)",
                        CommandTypes.EXECUTE, _phone)
                    logger.info("Contact deleted succesfully")
                    break
                elif choice.upper() == 'N':
                    break
    if not presence:
        logger.info("This contact is not present in phone book")
        logger.info("Exiting")


def retrieve_from_db(name: str) -> None:
    ls = sql_execute(
        "SELECT NAME, PHONE from PHONEBOOK",
        CommandTypes.EXECUTE)
    _flag = False
    for _, row in list(enumerate(ls)):
        if name in row[0]:
            _flag = True
            logger.info(f"{name} -> {row[1]}")
    if not _flag:
        logger.info("This contact is not present")
        logger.info("exiting")


def push_to_db(name: str, phone: int) -> None:
    ret = sql_execute(
        '''SELECT name FROM sqlite_master WHERE type='table' AND
        name='PHONEBOOK\'''',
        CommandTypes.CHECK
    )
    if not ret:
        sql_execute(
            '''CREATE TABLE PHONEBOOK(
            NAME TEXT NOT NULL,
            PHONE INT NOT NULL);''',
            CommandTypes.CREATE
        )
    response = sql_execute("SELECT * FROM PHONEBOOK", CommandTypes.EXECUTE)
    rows = list(response)
    numbers = []
    for _name, _phone in rows:
        if name == _name:
            numbers.append(str(_phone))
    if len(numbers) != 0:
        logger.info(f"Contact with the name {name} already present")
        logger.info(f"Saved numbers : {','.join([_ for _ in numbers])}")
        while True:
            choice = input(
                "Do you want to add this number to existing contact "
                "Y/N : ")
            if choice.upper() == 'Y':
                if phone != _phone:
                    sql_execute('''INSERT INTO PHONEBOOK (NAME,PHONE)
                    VALUES (?, ?);''', CommandTypes.EXECUTE, name, phone)
                    logger.info("Contact added")
                    break
                else:
                    logger.info("This phone is already added")
                    logger.info("Exiting the application....")
                    break
            elif choice.upper() == 'N':
                logger.info("Exiting the application.....")
                break
            else:
                logger.info("Unsupported character, please select Y/N")
    else:
        logger.info("Adding a new contact")
        sql_execute(
            '''INSERT INTO PHONEBOOK (NAME,PHONE)
                VALUES (?, ?);''', CommandTypes.EXECUTE, name, phone)
        logger.info("Contact added")


def application_header():
    print('='*50)
    print('{:=^50}'.format('PHONE BOOK'))
    print('{:=^50}'.format('Developed by : ©faris_kamal'))
    print('='*50)


def main():
    application_header()
    parser = argparse.ArgumentParser(
        prog="Contact Book",
        description="Application to store phone numbers",
        epilog="Developed by Faris Kamal",
    )
    parser.add_argument(
        "--name",
        help="Name of the contact"
    )
    parser.add_argument(
        "--phone",
        type=int,
        help="Phone number of the person you want to save"
    )
    parser.add_argument(
        "--r",
        help="This flag should be used for getting phone number",
        action='store_true'
    )
    parser.add_argument(
        "--u",
        help="This flag should be used for updating phone number",
        action='store_true'
    )
    parser.add_argument(
        "--d",
        help="This flag should be used for deleting a contact",
        action='store_true'
    )
    args = parser.parse_args()
    name, phone = args.name, args.phone
    if args.r:
        if args.name:
            retrieve_from_db(name)
    elif args.u:
        update_value_db(name, phone)
    elif args.d:
        delete_from_db(name)
    else:
        push_to_db(name, phone)


if __name__ == "__main__":
    main()
