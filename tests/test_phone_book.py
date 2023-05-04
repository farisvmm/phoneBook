import pytest
from phonebook import main



def test_sql_execute():
    cmd = "SELECT name FROM sqlite_master WHERE type='table' AND\
            name='PHONEBOOK\'"
    result = main.sql_execute(cmd)
    print("this is the result" + str(result))
    assert result

    cmd = "SELECT * FROM PHONEBOOK"
    result = main.sql_execute(cmd)
    print(result)
    assert result
