import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from data_store import add_users, insert_users
from config import comunity_token, acces_token
from main import VkTools

class BotInterface:

    def __init__(self, comunity_token, acces_token):
        self.interface = vk_api.VkApi(token=comunity_token)
        self.api = VkTools(acces_token)
        self.params = None
        self.offset = 0
        self.longpoll = VkLongPoll(self.interface)

    def message_send(self, user_id, message, attachment=None):
        self.interface.method('messages.send',
                              {'user_id': user_id,
                               'message': message,
                               'attachment': attachment,
                               'random_id': get_random_id()
                               }
                              )
        
    def get_info_from_user(self, user_id):
        
        user_data = self.api.get_profile_info(user_id)
        if user_data['city'] is None:
            self.message_send(user_id, 'У Вас не указан город проживания. Укажите свой город')
            user_city = self.wait_for_user_response(user_id)
            city_user = self.api.get_city(user_city)
            user_data['city'] = city_user

        elif user_data['bdate'] is None:
            self.message_send(user_id, 'У Вас не указана дата рождения. Укажите дату рождения в формате ДД.ММ.ГГГГ')
            bdate_response = self.wait_for_user_response(user_id)
            user_data['bdate'] = bdate_response    

        elif user_data['sex'] is None:
            self.message_send(user_id, 'У Вас не указан полУкажите свой пол (1 - женский, 2 - мужской)')
            gender_response = self.wait_for_user_response(user_id)
            user_data['sex'] = int(gender_response)

        return user_data    


    def wait_for_user_response(self, user_id):
        for event in  self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.user_id == user_id:
                return event.text        

    def event_handler(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()
                if command == 'привет':
                    self.params = self.get_info_from_user(event.user_id)
                    self.message_send(event.user_id, f'Привет {self.params["name"]}, это бот по поиску партнёра. Введите "Поиск" для поска партнёра')
                elif command == 'поиск':
                    if self.params is None:
                        self.message_send(event.user_id, f'Для начала необходимо написать "Привет" ')                      
                    elif self.params is not None:
                        users = self.api.search_users(self.params, self.offset)
                        self.offset += 10
                        user = users.pop()
                        while insert_users(user["id"]):
                            user = users.pop()
                        if user['is_closed']:
                            self.message_send(event.user_id,
                                            f'Профиль {user["name"]}, vk.com/id{user["id"]} закрыт, надо искать дальше'
                                                )
                            add_users(user['id'], event.user_id)
                        else:
                            photos_user = self.api.get_photos(user['id'])
                            attachment = ''
                            for num, photo in enumerate(photos_user):
                                attachment += f'photo{user["id"]}_{photo["id"]},'
                                if num == 2:
                                    break
                            self.message_send(event.user_id,
                                            f'Встречайте {user["name"]}, vk.com/id{user["id"]}',
                                            attachment=attachment
                                            )
                            add_users(user["id"], event.user_id)
                else:
                    self.message_send(event.user_id, f'Напишите "поиск" для поиска партнёра.')


if __name__ == '__main__':
    bot = BotInterface(comunity_token, acces_token)
    bot.event_handler()