from datetime import datetime
from config import acces_token
import vk_api

class VkTools():
    def __init__(self, acces_token):
        self.api = vk_api.VkApi(token=acces_token)

    def get_profile_info(self, user_id):

        info, = self.api.method('users.get',
                            {'user_id': user_id,
                            'fields': 'city,bdate,sex,relation,home_town' 
                            }
                            )
        user_info = {'name': info['first_name'] + ' '+ info['last_name'],
                     'id':  info['id'],
                     'bdate': info['bdate'] if 'bdate' in info else None,
                     'home_town': info['home_town'],
                     'sex': info['sex'],
                     'city': info['city']['id'] if 'city' in info else None
                     }
        return user_info

    def search_users(self, params, offset):

        sex = 1 if params['sex'] == 2 else 2
        city = params['city']
        curent_year = datetime.now().year
        user_year = int(params['bdate'].split('.')[2])
        age = curent_year - user_year
        age_from = age - 1
        age_to = age + 1

        users = self.api.method('users.search',
                                {'count': 50,
                                 'offset': offset,
                                 'age_from': age_from,
                                 'age_to': age_to,
                                 'sex': sex,
                                 'city': city,
                                 'status': 6,
                                 'has_photo': True,
                                 'is_closed': False,
                                 'can_access_closed': True
                                 }
                                )
        try:
            users = users['items']
        except KeyError:
            return []

        res = []

        for user in users:
            res.append({'id': user['id'],
                        'name': user['first_name'] + ' ' + user['last_name'],
                        'is_closed': user['is_closed']
                        }
                        )

        return res
    
    def get_photos(self, user_id):
        photos = self.api.method('photos.get',
                                 {'user_id': user_id,
                                  'album_id': 'profile',
                                  'extended': 1
                                  }
                                 )
        try:
            photos = photos['items']
        except KeyError:
            return []

        res = []

        for photo in photos:
            res.append({'owner_id': photo['owner_id'],
                        'id': photo['id'],
                        'likes': photo['likes']['count'],
                        'comments': photo['comments']['count'],
                        }
                       )

        res.sort(key=lambda x: x['likes'] + x['comments'] * 10, reverse=True)
        return res

    def get_city(self, city_name):
        cities = self.api.method("database.getCities",
                                 {'items': 0,
                                  'q': city_name,
                                  'count': 1,
                                  'offset': 0,
                                  }
                                 )
        try:
            cities = cities['items']
        except KeyError:
            return []
        for city in cities:
            res = city['id']
            return res

if __name__ == '__main__':
    bot = VkTools(acces_token)
    params = bot.get_profile_info(63267424)
    users = bot.search_users(params)