from dataclasses import dataclass


@dataclass
class UserQueryObject:
    before_cleaning_user_txt: str = ''
    after_cleaning_user_txt: str = ''
    discovered_cmd: str = ''
    final_cmd: str = ''
    original_txt: str = ''
    key_word: str = ''
    answer: str = ''
    percent: int = 0
