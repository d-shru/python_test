#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""Нужно привести файл банковской выписки к виду,
   пригодному для загрузки в программу учёта финансов,
   представить строки в виде:

   2018-11-21;;-1940,90;Транспорт:Общественный транспорт;Метро;C;
"""

import re
import csv
import argparse
from datetime import datetime


def search_date(line):
    """ Ищем все даты в строке и загоняем в список. Дат может быть
    несколько: дата совершения операции, дата поступления платежа и
    дата подтверждения банком. Нас интересует дата совершения операции,
    поэтому берём последний элемент списка.
    """
    date_list = re.findall('\d{2}\.\d{2}\.\d{4}|\d{2}\.\d{2}\.\d{2}', line)
    date_found = date_list.pop()
    return date_found


def date_forward(line):
    """ Функция, приводящая дату в нужный формат.
    В некоторых датах год в формате 'YYYY', поэтому ловим исключение
    """
    try:
        date_forwarded = datetime.strptime(search_date(line), '%d.%m.%y')
    except ValueError:
        date_forwarded = datetime.strptime(search_date(line), '%d.%m.%Y')
    date_forwarded = datetime.date(date_forwarded)
    return date_forwarded


def date_reverse(line):
    """ В некоторых строках даты инвертированы.
    Приводим к нужному формату.
    """
    date_reversed = datetime.strptime(search_date(line), '%y.%m.%d')
    date_reversed = datetime.date(date_reversed)
    return date_reversed


def price_find(line):
    """ Находим в строке цену: разбиваем строку по разделителю и создаём
    список. Цена содержится в последнем элементе списка. Если последний
    элемент списка == 0, то берём предыдущий элемент
    """
    price_list = line.split(';')
    if price_list[-1] == '0':
        price_found = price_list[-2]
    else:
        price_found = price_list[-1]
    return price_found


def price_convert(line):
    """ Приводим цену к нужному виду:
    Ищем в цене разделитель, если нет, то добавляем ',00'
    Если после разделителя - одна цифра, то то добавляем '0'
    Если не поступление, то добавляем перед ценой '-'
    """
    price = price_find(line)
    if ',' not in price:
        price += ',00'
    else:
        if re.findall(',\S{2}', price) == []:
            price += '0'

    if 'Основание' not in line and 'командиров' not in line:
        price = "-" + price
    return price


def dict_rplace(line):
    """ Сопоставляем каждую строку файла с каждым ключом словаря,
    т.е. берём ключ - ищем в строке, если нет совпадения,то пишем в
    переменную '**'. Если есть совпадение - пишем значение ключа.
    """
    for dict_key in dct.keys():
        if dict_key in line:
            rplace = dct[dict_key]
            break
        else:
            rplace = "**"
    return rplace


def line_convert():
    """Открываем файл для конвертирования и подготавливаем его
    """
    with open(args.file, 'r') as file_to_convert:
        for line in file_to_convert:
            line = line.rstrip()
            if line.endswith('.') is True:
                line = line[:-1]
            if line.endswith(';') is True:
                line = line[:-1]

            # Если сумма на удержании банком, то дата стоит в виде: yy.mm.dd
            if ';HOLD;' not in line:
                date = date_forward(line)
            else:
                date = date_reverse(line)

            price = price_convert(line)
            date = str(date)
            rplace = dict_rplace(line)

            #line_final = date + ";;" + price + ";" + rplace
            line_final = f'{date};;{price};{rplace}'

            """ Формируем сконвертированный файл. В случае, если не всe
            точки оплаты присутствуют в словаре, то выводим их на stdout
            """
            file_result.write(line_final + '\n')
            if '**' in line_final:
                print (line)
    return line_final


parser = argparse.ArgumentParser(description='File to convert, and file dict')

parser.add_argument(
        '-f',
        '--file',
        type=str,
        default='to_convert.csv',
        help='Input filename to convert')

parser.add_argument(
        '-d',
        '--dict',
        type=str,
        default='dict.csv',
        help='Input dict filename')

parser.add_argument(
        '-r',
        '--result',
        type=str,
        default='transcoded_alfa.csv',
        help='Input filename for output result')

args = parser.parse_args()


""" Открываем список "точки_олаты-категория" для передачи в словарь."""
with open(args.dict, 'r') as file_dict:
    dct = eval(file_dict.read())  # TODO избавится от eval используя import csv

with open(args.result, 'w') as file_result:
    line_convert()

