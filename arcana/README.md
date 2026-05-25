# Кодекс Нитей — магическая система на Python

Проект демонстрирует 4 принципа ООП: инкапсуляцию, наследование, полиморфизм и абстракцию.

## Запуск

```bash
cd src
python main.py
```

## Тесты

```bash
pip install -r requirements.txt
coverage run -m pytest tests/ -v
coverage report -m
pytest --html=report.html --self-contained-html
```

## Структура

```
project/
├── src/
│   ├── threads.py
│   ├── spells.py
│   ├── artifacts.py
│   ├── caster.py
│   └── main.py
├── tests/
│   └── test_algorithms.py
├── requirements.txt
├── ARCHITECTURE.md
└── README.md
```
