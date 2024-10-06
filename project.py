import os
import pandas as pd


class PriceMachine:

    def __init__(self):
        self.data = []  # Хранит данные о продуктах
        self.result = ''  # Для вывода результатов поиска
        self.name_length = 0  # Длина названия продукта для форматирования вывода

    def load_prices(self, directory='.'):
        '''
            Сканирует указанный каталог. Ищет файлы со словом "price" в названии.
            В каждом файле ищет столбцы с названием товара, ценой и весом.
        '''
        price_files = []  # Список для хранения файлов с ценами
        for filename in os.listdir(directory):
            if 'price' in filename.lower() and filename.endswith('.csv'):
                price_files.append(filename)  # Добавляем файл в список

        # Выводим списки найденных файлов в консоль
        if price_files:
            print("Найденные файлы с прайс-листами:")
            for file in price_files:
                print(f" - {file}")
        else:
            print("Не найдено файлов с прайс-листами.")

        # Загружаем данные из найденных файлов
        for filename in price_files:
            self._load_file(os.path.join(directory, filename))

    def _load_file(self, file_path):
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig', delimiter=',')
            print(f"Заголовки для файла {file_path}: {df.columns.tolist()}")  # Вывод заголовков

            # Определяем возможные названия столбцов
            valid_name_variants = ["название", "продукт", "товар", "наименование"]
            valid_price_variants = ["цена", "розница"]
            valid_weight_variants = ["фасовка", "масса", "вес"]

            # Очищаем заголовки: убираем лишние символы
            cleaned_headers = [col.strip().lower().replace('#', '').replace(',,', '') for col in df.columns]

            # Ищем имена действительных столбцов в очищенных заголовках
            name_col = next((col for col in cleaned_headers if col in valid_name_variants), None)
            price_col = next((col for col in cleaned_headers if col in valid_price_variants), None)
            weight_col = next((col for col in cleaned_headers if col in valid_weight_variants), None)

            if name_col is None:
                print(f"Не удалось найти столбец с названием товара в файле: {file_path}")
                return
            if price_col is None:
                print(f"Не удалось найти столбец с ценой в файле: {file_path}")
                return
            if weight_col is None:
                print(f"Не удалось найти столбец с весом в файле: {file_path}")
                return

            # Заполняем данные
            for index, row in df.iterrows():
                name = row[name_col]
                price = row[price_col]
                weight = row[weight_col]
                price_per_kg = price / weight if weight != 0 else 0
                self.data.append({
                    'name': name,
                    'price': price,
                    'weight': weight,
                    'file': file_path,
                    'price_per_kg': price_per_kg
                })
                self.name_length = max(self.name_length, max(len(str(name)), len(str(price)), len(str(weight))))

        except Exception as e:
            print(f"Ошибка при загрузке файла {file_path}: {e}")

    def _search_product_price_weight(self, headers):
        '''
            Возвращает номера столбцов
        '''
        name_col = next((idx for idx, h in enumerate(headers) if h in ['товар', 'название', 'наименование', 'продукт']),
                        None)
        price_col = next((idx for idx, h in enumerate(headers) if h in ['розница', 'цена']), None)
        weight_col = next((idx for idx, h in enumerate(headers) if h in ['фасовка', 'масса', 'вес']), None)
        return name_col, price_col, weight_col

    def find_text(self, text):
        # Приводим текст к нижнему регистру
        text = text.lower()
        filtered_data = [
            item for item in self.data
            if text in item['name'].lower()
        ]

        print(f'Найдено {len(filtered_data)} позиций по запросу "{text}".')
        return sorted(filtered_data, key=lambda x: x['price_per_kg'])

    def export_to_html(self, fname='output.html'):
        '''
            Экспортирует данные в HTML файл
        '''
        result = '''
        <meta charset="UTF-8">
        <!DOCTYPE html>
        <html>
        <head>
            <title>Позиции продуктов</title>
            <style>
                table {
                    width: 100%;
                    border-collapse: collapse;
                }
                th, td {
                    border: 1px solid black;
                    padding: 8px;
                    text-align: left;
                }
                th {
                    background-color: #f2f2f2;
                }
            </style>
        </head>
        <body>
            <table>
                <tr>
                    <th>Номер</th>
                    <th>Название</th>
                    <th>Цена</th>
                    <th>Фасовка</th>
                    <th>Файл</th>
                    <th>Цена за кг.</th>
                </tr>
        '''

        for i, item in enumerate(self.data, start=1):
            result += f'''
                <tr>
                    <td>{i}</td>
                    <td>{item['name']}</td>
                    <td>{item['price']}</td>
                    <td>{item['weight']}</td>
                    <td>{item['file']}</td>
                    <td>{item['price_per_kg']:.2f}</td>
                </tr>
            '''

        result += '''
            </table>
        </body>
        </html>
        '''

        with open(fname, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f'Данные экспортированы в {fname}')


# Логика работы программы
pm = PriceMachine()

directory = input("Введите путь к директории с прайс-листами (по умолчанию текущая директория): ") or '.'
pm.load_prices(directory)  # Загружаем прайс-листы

while True:
    search_text = input('Введите текст для поиска или "exit" для выхода: ')
    if search_text.lower() == 'exit':
        break
    results = pm.find_text(search_text)
    if results:
        print(f"{'№':<5} {'Название':<{pm.name_length}} {'Цена':<10} {'Фасовка':<10} {'Файл':<15} {'Цена за кг.':<15}")
        for idx, item in enumerate(results, start=1):
            print(
                f"{idx:<5} {item['name']:<{pm.name_length}} {item['price']} {item['weight']} {item['file']} {item['price_per_kg']:.2f}")
    else:
        print('Нет найденных позиций.')

print('Завершение работы программы.')
pm.export_to_html()  # Экспортируем в HTML
