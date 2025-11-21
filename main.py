import random
import json
import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

# Игроки
players = {
    'Player 1': {'name': 'Player 1', 'balance': 5000, 'history': [], 'wins': 0, 'games': 0},
    'Player 2': {'name': 'Player 2', 'balance': 5000, 'history': [], 'wins': 0, 'games': 0},
    'Player 3': {'name': 'Player 3', 'balance': 5000, 'history': [], 'wins': 0, 'games': 0},
}


# Выбор игрока
class PlayerSelectionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        label = Label(text='Выберите игрока:', font_size=24)
        layout.add_widget(label)

        for name in players.keys():
            button = Button(text=name, font_size=20)
            button.bind(on_release=lambda inst, n=name: self.select_player(n))
            layout.add_widget(button)

        self.add_widget(layout)

    def select_player(self, player_name):
        main_game_screen = self.manager.get_screen('main_game')
        main_game_screen.set_player(player_name)
        self.manager.current = 'main_game'


# Мини-игра: Угадать число
class GuessNumberScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        label = Label(text='Угадать число от 1 до 100', font_size=24)
        layout.add_widget(label)
        self.guess_input = TextInput(multiline=False, input_filter='int', font_size=20)
        layout.add_widget(self.guess_input)
        self.result_label = Label(text='', font_size=20)
        layout.add_widget(self.result_label)
        try_again_btn = Button(text='Попробовать ещё раз', size_hint=(1, 0.2))
        try_again_btn.bind(on_release=self.start_game)
        layout.add_widget(try_again_btn)
        self.add_widget(layout)
        self.start_game()

    def start_game(self, *args):
        self.secret_number = random.randint(1, 100)
        self.result_label.text = ''
        self.guess_input.text = ''

    def check_guess(self, instance):
        try:
            guess = int(self.guess_input.text)
        except ValueError:
            self.result_label.text = 'Введите целое число!'
            return

        current_screen = self.manager.get_screen('main_game')  # Получение главного экрана
        balance = current_screen.player_data['balance']
        bet_amount = current_screen.current_bet

        if balance >= bet_amount:
            if guess == self.secret_number:
                winnings = bet_amount * 2  # Удваиваем ставку
                current_screen.player_data['balance'] += winnings
                current_screen.player_data['wins'] += 1
                self.result_label.text = f'Правильно! Ваш выигрыш: {winnings}. Баланс обновлён.'
            else:
                current_screen.player_data['balance'] -= bet_amount
                self.result_label.text = f'Неправильно! Минус {bet_amount}, попробуйте ещё раз.'

            current_screen.update_display()  # Обновляем интерфейс
        else:
            self.result_label.text = 'Недостаточно средств для продолжения игры.'


# Мини-игра: Рулетка
class RouletteScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        label = Label(text='Рулетка', font_size=24)
        layout.add_widget(label)
        self.spin_btn = Button(text='Крутить рулетку', font_size=20)
        self.spin_btn.bind(on_release=self.spin_wheel)
        layout.add_widget(self.spin_btn)
        self.result_label = Label(text='', font_size=20)
        layout.add_widget(self.result_label)
        self.bonus_label = Label(text='', font_size=18)
        layout.add_widget(self.bonus_label)
        self.add_widget(layout)

    def spin_wheel(self, instance):
        current_screen = self.manager.get_screen('main_game')
        balance = current_screen.player_data['balance']
        bet_amount = current_screen.current_bet

        if balance >= bet_amount:
            result = random.randint(0, 36)
            self.result_label.text = f'Результат: {result}'

            # Проверяем бонусы и выигрыши
            if result % 2 == 0:  # Пример простого условия выигрыша
                winnings = bet_amount * 2
                current_screen.player_data['balance'] += winnings
                current_screen.player_data['wins'] += 1
                self.result_label.text += f'\nВы выиграли {winnings}!'
            else:
                current_screen.player_data['balance'] -= bet_amount
                self.result_label.text += '\nВы проиграли свою ставку.'

            current_screen.update_display()  # Обновляем интерфейс
        else:
            self.result_label.text = 'Недостаточно средств для вращения рулетки.'


# Мини-игра: Бомбер (6x6)
class BomberScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_x = 6
        self.size_y = 6
        self.bombs = 6
        self.multipliers = [2, 3, 5, 10, 20]
        self.field = []
        self.buttons = []
        self.bombs_positions = set()
        self.init_game()

    def start_game(self):
        self.clear_widgets()
        self.init_game()

    def init_game(self):
        self.bombs_positions = set(random.sample(range(self.size_x * self.size_y), self.bombs))
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        info_label = Label(text='Бомбер 6x6: выберите клетку', font_size=20)
        layout.add_widget(info_label)
        grid = GridLayout(cols=self.size_x, rows=self.size_y, spacing=2)
        self.buttons = []

        for i in range(self.size_x * self.size_y):
            btn = Button(text='?', font_size=14)
            btn.index = i
            btn.bind(on_release=self.open_cell)
            self.buttons.append(btn)
            grid.add_widget(btn)

        layout.add_widget(grid)
        self.add_widget(layout)

    def open_cell(self, instance):
        idx = instance.index
        if idx in self.bombs_positions:
            instance.text = '💣'
            instance.background_color = (1, 0, 0, 1)
            self.game_over(False)
        else:
            multiplier = random.choice(self.multipliers)
            instance.text = f'x{multiplier}'
            instance.background_color = (0, 1, 0, 1)
            self.process_multiplier(multiplier)

    def process_multiplier(self, multiplier):
        current_screen = self.manager.get_screen('main_game')
        balance = current_screen.player_data['balance']
        bet_amount = current_screen.current_bet

        if balance >= bet_amount:
            winnings = bet_amount * multiplier
            current_screen.player_data['balance'] += winnings
            current_screen.player_data['wins'] += 1
            current_screen.update_display()
        else:
            print("Недостаточно средств.")

    def game_over(self, win):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=10)
        message = 'Победа!' if win else 'Проигрыш!'
        layout.add_widget(Label(text=message, font_size=24))
        back_btn = Button(text='Назад', size_hint=(1, 0.2))
        back_btn.bind(on_release=self.back_to_menu)
        layout.add_widget(back_btn)
        self.add_widget(layout)

    def back_to_menu(self, instance):
        self.manager.current = 'main_game'
        self.clear_widgets()


# Простая покер-игра
class PokerScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10)
        label = Label(text='Простой покерный матч', font_size=24)
        layout.add_widget(label)
        self.play_btn = Button(text='Играйте!', size_hint=(1, 0.2))
        self.play_btn.bind(on_release=self.play_poker)
        layout.add_widget(self.play_btn)
        self.result_label = Label(text='', font_size=20)
        layout.add_widget(self.result_label)
        self.add_widget(layout)

    def play_poker(self, instance):
        current_screen = self.manager.get_screen('main_game')
        balance = current_screen.player_data['balance']
        bet_amount = current_screen.current_bet

        if balance >= bet_amount:
            if random.random() < 0.5:
                winnings = bet_amount * 2
                current_screen.player_data['balance'] += winnings
                current_screen.player_data['wins'] += 1
                self.result_label.text = f'Вы победили! Ваш выигрыш составил {winnings}.'
            else:
                current_screen.player_data['balance'] -= bet_amount
                self.result_label.text = 'Вы проиграли раунд.'

            current_screen.update_display()
        else:
            self.result_label.text = 'Недостаточный баланс для участия в раунде.'


# Меню выбора мини-игр
class MiniGameSelectScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text='Выбор мини-игры:', font_size=24))
        poker_btn = Button(text='Покер', font_size=20)
        roulette_btn = Button(text='Рулетка', font_size=20)
        guess_btn = Button(text='Угадать число', font_size=20)
        bomber_btn = Button(text='Бомбер (6x6)', font_size=20)

        poker_btn.bind(on_release=lambda inst: self.open_game('poker'))
        roulette_btn.bind(on_release=lambda inst: self.open_game('game'))  # Рулетка
        guess_btn.bind(on_release=lambda inst: self.open_game('guess_number'))
        bomber_btn.bind(on_release=lambda inst: self.open_game('bomber'))

        layout.add_widget(poker_btn)
        layout.add_widget(roulette_btn)
        layout.add_widget(guess_btn)
        layout.add_widget(bomber_btn)
        self.add_widget(layout)

    def open_game(self, screen_name):
        self.manager.current = screen_name


# Главное игровое меню
class MainGameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.player_name = None
        self.player_data = None
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        top_panel = BoxLayout(size_hint=(1, 0.2), spacing=10)
        self.player_label = Label(text='Игрок: ', font_size=20)
        self.balance_label = Label(text='Баланс: ', font_size=20)
        self.bet_label = Label(text='Ставка: ', font_size=20)
        self.change_player_btn = Button(text='Сменить игрока', size_hint=(0.3, 1))
        self.change_player_btn.bind(on_release=self.change_player)
        self.edit_name_btn = Button(text='Изменить имя', size_hint=(0.3, 1))
        self.edit_name_btn.bind(on_release=self.edit_name)

        top_panel.add_widget(self.player_label)
        top_panel.add_widget(self.balance_label)
        top_panel.add_widget(self.bet_label)
        top_panel.add_widget(self.change_player_btn)
        top_panel.add_widget(self.edit_name_btn)

        bet_container = BoxLayout(size_hint=(1, 0.1))
        self.bet_input = TextInput(text='10', multiline=False, input_filter='int', size_hint=(0.3, 1))
        self.bet_input.bind(on_text_validate=self.on_bet_input)
        self.bet_input.bind(focus=self.on_bet_focus)
        bet_container.add_widget(Label(text='Ваша ставка:', font_size=16))
        bet_container.add_widget(self.bet_input)

        choose_game_btn = Button(text='Выбрать мини-игру', size_hint=(1, 0.1))
        choose_game_btn.bind(on_release=self.open_minigame_menu)

        stats_box = BoxLayout(size_hint=(1, 0.2))
        self.next_win_chance_label = Label(text='Шансы на победу: ', font_size=16)
        self.next_bet_estimate_label = Label(text='Рекомендуемая ставка: ', font_size=16)
        self.update_stats_button = Button(text='Рассчитать шансы', size_hint=(0.3, 1))
        self.update_stats_button.bind(on_release=self.calculate_next_shots)
        stats_box.add_widget(self.next_win_chance_label)
        stats_box.add_widget(self.next_bet_estimate_label)
        stats_box.add_widget(self.update_stats_button)

        layout.add_widget(top_panel)
        layout.add_widget(bet_container)
        layout.add_widget(choose_game_btn)
        layout.add_widget(stats_box)

        self.add_widget(layout)
        self.current_bet = 10

    def set_player(self, player_name):
        self.player_name = player_name
        self.player_data = players[player_name]
        self.current_bet = 10
        self.update_display()
        self.calculate_next_shots(None)

    def update_display(self):
        self.player_label.text = f'Игрок: {self.player_name}'
        self.balance_label.text = f'Баланс: {self.player_data["balance"]}'
        self.bet_label.text = f'Ставка: {self.current_bet}'
        self.bet_input.text = str(self.current_bet)
        self.next_win_chance_label.text = f'Шансы на победу: {(self.player_data["wins"] / (self.player_data["games"] + 1)) * 100:.1f}%'
        recommended_bet = min(max(int(self.player_data["balance"] * 0.1), 1), self.player_data["balance"])
        self.next_bet_estimate_label.text = f'Рекомендуемая ставка: {recommended_bet}'

    def change_player(self, instance):
        self.manager.current = 'player_select'

    def edit_name(self, instance):
        self.new_name = TextInput(multiline=False, text=self.player_name)
        self.new_name.bind(on_text_validate=self.save_new_name)
        self.add_widget(self.new_name)
        self.new_name.focus = True

    def save_new_name(self, instance):
        new_name = instance.text.strip()
        if new_name and new_name != '':
            old_name = self.player_name
            players[new_name] = players.pop(old_name)
            self.player_name = new_name
            self.player_data = players[self.player_name]
            self.update_display()
        self.remove_widget(self.new_name)

    def on_bet_input(self, instance):
        try:
            bet = int(instance.text)
        except ValueError:
            bet = self.current_bet
        if bet < 1 or bet > self.player_data['balance']:
            bet = self.current_bet
        self.current_bet = bet
        self.bet_input.text = str(self.current_bet)
        self.bet_label.text = f'Ставка: {self.current_bet}'

    def on_bet_focus(self, instance, focus):
        if not focus:
            self.on_bet_input(instance)

    def open_minigame_menu(self, instance):
        self.manager.current = 'minigame_select'

    def calculate_next_shots(self, instance):
        games_count = self.player_data['games']
        wins_count = self.player_data['wins']
        if games_count > 0:
            win_probability = wins_count / games_count
        else:
            win_probability = 0.3
        self.next_win_chance_label.text = f'Шансы на победу: {win_probability * 100:.1f}%'
        recommend_bet = max(1, int(self.player_data['balance'] * 0.1))
        self.next_bet_estimate_label.text = f'Рекомендуемая ставка: {recommend_bet}'


# Основной класс приложения
class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(PlayerSelectionScreen(name='player_select'))
        sm.add_widget(MainGameScreen(name='main_game'))
        sm.add_widget(MiniGameSelectScreen(name='minigame_select'))
        sm.add_widget(PokerScreen(name='poker'))
        sm.add_widget(RouletteScreen(name='game'))
        sm.add_widget(GuessNumberScreen(name='guess_number'))
        sm.add_widget(BomberScreen(name='bomber'))
        return sm


if __name__ == '__main__':
    MyApp().run()