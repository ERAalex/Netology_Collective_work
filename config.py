import configparser

config = configparser.ConfigParser()
config.read('settings.ini')
token_user = config['VKONTAKTE']['token_user']
token_community = config['VKONTAKTE']['token_community']
postgres_username = config['DATABASE']['username']
postgres_password = config['DATABASE']['password']