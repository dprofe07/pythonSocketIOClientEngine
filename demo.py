from client import Client


class MyClient2(Client):
    @Client.io_event('MyClient2', 'new_user')
    def added_user(self, data):
        print(f'Добавился пользователь: {data["login"]}')

    @Client.io_event('MyClient2', 'winner')
    def there_is_winner(self, data):
        global continue_
        print(f'Игрок {data["login"]} победил!!! Мы загадывали число: {data["n"]}')
        cl.disconnect()
        exit(0)

host = ('127.0.0.1', 5000), ('91.204.57.48', 8007)
print('Выбирите сервер')
print('1. localhost')
print('2. test server')
a = input()

if a == '1':
    host = host[0]
else:
    host = host[1]
cl = MyClient2(*host)
cl.connect()

print('Игра угадай число.')

print('От 1 до 100')

game_id = input('Индентификартор игры: ')

login = input('Ваш логин: ')

cl.emit('join', {'login': login, 'game_id': game_id})

join_ans = cl.wait_for('join_answer')

if join_ans['joined']:
    print('Успешно присоединились!')
else:
    print('BAD')
    cl.disconnect()
    exit(1)

if join_ans['created']:
    print('Ожидание других пользователей. Чтобы закрыть комнату и начать игру, нажмите Enter')
    input()
    cl.emit('close_room', {})
else:
    print('Ждём других игроков')

cl.wait_for('start_game')

continue_ = True

while continue_:
    a = int(input('Ваше предположение: '))
    cl.emit('check_number', {'n': a})
    print('Wait for ans')
    ans = cl.wait_for('answer')
    if ans['result'] == 'less':
        print("Загаданное число меньше")
    elif ans['result'] == 'greater':
        print('Загаданное число больше')
    elif ans['result'] == 'equals':
        print('Вы угадали!')
        break


cl.disconnect()