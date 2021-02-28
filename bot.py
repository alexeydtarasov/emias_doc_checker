import pandas as pd

from telebot import TeleBot
from selenium import webdriver

from time import sleep

import dataparser


class Bot:
    def __init__(self, token, buff_path):
        self.bot = TeleBot(token)
        self.buff_path = buff_path
        self.users = pd.read_csv(buff_path, delimiter=';',
                                 parse_dates=['birth_date', ],
                                 converters={'police_number': str})

    def alert(self, user: pd.DataFrame, result_data: pd.DataFrame):
        msg = f"Запись к <b>{user['doc_name']}</b> доступна!\n"
        msg += f"- С: <b>{result_data['nearest_date'].values[0]}</b>\n"
        msg += f'- Адрес: <b>{result_data["address"].values[0]}</b>\n'
        msg += f'- Кабинет: <b>{result_data["room"].values[0]}</b>'
        self.bot.send_message(user['chat_id'], msg, parse_mode="HTML")

    def authorize(self, user: pd.DataFrame):
        polis_wp = self.driver.find_element_by_name('policy-number')
        d_wp = self.driver.find_element_by_name('day')
        m_wp = self.driver.find_element_by_name('month')
        y_wp = self.driver.find_element_by_name('year')

        polis_wp.send_keys(user['police_number'])
        d, m, y = tuple(user['birth_date'].strftime('%d.%m.%Y').split('.'))
        d_wp.send_keys(d)
        m_wp.send_keys(m)
        y_wp.send_keys(y)
        sleep(5)

        self.driver.find_element_by_class_name('_3ZwLuw').submit()
        sleep(30)

    def check_for_user(self, user: pd.DataFrame, index: int) -> pd.DataFrame:
        self.driver.get('https://emias.info/')
        sleep(15)

        self.authorize(user)

        for i in range(5):
            try:
                self.go_to_specialists(user)
                break
            except AttributeError:
                sleep(5)

        result_data = dataparser.parse_all_doctors(self.driver.page_source)

        if user['doc_name'] in result_data['doc_name'].unique():
            result_data = result_data.loc[
                    result_data['doc_name'] == user['doc_name'], :]
            self.alert(user, result_data)
            self.delete_user(index)

        self.driver.close()

    def delete_user(self, index):
        self.users.drop(index, inplace=True)
        self.users.to_csv(self.buff_path, index=False)
        print(self.users)

    def go_to_specialists(self, user: pd.DataFrame):

        specialists = self.driver.find_elements_by_class_name('_9Ki6B-')

        spec_button = dataparser.find_specialist(specialists, user['doc_type'])
        spec_button.click()
        sleep(10)

        # уберем вылезающее окошко (иногда)
        try:
            okno = self.driver.find_element_by_class_name('_1U2vgr')
            okno.find_elements_by_class_name('_3ZwLuw')[-1].click()
            sleep(5)
        except:
            pass

    def loop(self):
        while True:

            self.driver = webdriver.Firefox()
            sleep(5)

            for index, user in self.users.iterrows():

                self.check_for_user(user, index)

            self.driver.quit()

            sleep(5)