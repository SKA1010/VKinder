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

    def message_send(self, user_id, message, attachment=None):
        self.interface.method('messages.send',
                              {'user_id': user_id,
                               'message': message,
                               'attachment': attachment,
                               'random_id': get_random_id()
                               }
                              )

    def event_handler(self):
        global photo, user, users
        longpoll = VkLongPoll(self.interface)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()

                if command == 'привет':
                    self.params = self.api.get_profile_info(event.user_id)
                    self.message_send(event.user_id, f'Привет {self.params["name"]}, это бот по поиску партнёра.')
                elif command == 'поиск':
                    if self.params is None:
                        self.message_send(event.user_id, f'Для начала необходимо написать "Привет" ')
                    else:
                        users = self.api.search_users(self.params, self.offset)
                        self.offset += 30
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
                    self.message_send(event.user_id, f'Команда не опознана! Напишите "поиск" для поиска партнёра.')


if __name__ == '__main__':
    bot = BotInterface(comunity_token, acces_token)
    bot.event_handler()