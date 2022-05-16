from sqlalchemy.exc import NoSuchColumnError

from database import *


#TODO add output info
@eel.expose
def calculate_centiles(last_name, first_name, dad_name, gender, dob, doi, body_length, body_weight, ind_ketle, c_chest,
                       c_waist, c_r_shoulders, c_l_shoulders, c_hips, c_neck, c_wrist, lungs_capacity, d_r_wrist,
                       d_l_wrist, systolic_pressure, diastolic_pressure, heart_rate, t_stomach, t_shoulder, t_back):
    for i in [body_length, body_weight, ind_ketle, c_chest, c_waist, c_r_shoulders, c_l_shoulders, c_hips, c_neck,
              c_wrist, lungs_capacity, d_r_wrist, d_l_wrist, systolic_pressure, diastolic_pressure, heart_rate,
              t_stomach, t_shoulder, t_back]:
        try:
            int(i)
            continue
        except:
            return 'Вы ввели некорректно численное значение'

    dob = datetime.strptime(dob, "%Y-%m-%d")
    doi = datetime.strptime(doi, "%Y-%m-%d")
    age = determine_the_passport_age(dob, doi)
    table = choose_table(age, gender)
    
    length_centile = get_centiles(table, 'Длина тела', body_length)
    weight_centile = get_centiles(table, 'Индекс Кетле', ind_ketle)
    if not weight_centile:
        weight_centile = get_centiles(table, 'Масса тела', body_weight)

    result = ''
    
    if 2 <= length_centile <= 7 and 3 <= weight_centile <= 6:
        result = "Нормальное физическое развитие."
    elif 2 <= length_centile <= 7 and 7 <= weight_centile <= 8:
        result = "Отклонения в развитии: Повышенная и высокая масса тела."
    elif 2 <= length_centile <= 7 and 1 <= weight_centile <= 2:
        result = "Отклонения в развитии: Сниженная и низкая масса тела."
    elif length_centile == 8:
        result = "Отклонения в развитии: Высокая длина."
    elif length_centile == 1:
        result = "Отклонения в развитии: Низкая длина тела."

    result += '<br/>Пропорциональность развития по ИМТ: '

    if 3 <= weight_centile <= 6:
        result += 'Гармоничное. '
    else:
        result += 'Дисгармоничное. '

    result += '<br/>Показатели ЖЕЛ, динамометрии: '

    lungs_capacity_centile = get_centiles(table, 'Жизненная ёмкость лёгких', lungs_capacity)
    d_r_wrist_centile = get_centiles(table, 'Динамометрия правой кисти', d_r_wrist)
    d_l_wrist_centile = get_centiles(table, 'Динамометрия левой кисти', d_l_wrist)

    if all([lungs_capacity_centile, d_r_wrist_centile, d_l_wrist_centile]):
        if lungs_capacity_centile <= 2 and d_l_wrist_centile <= 2 and d_r_wrist_centile <= 2:
            result += 'Дисгармоничное. '
        else:
            result += 'Гармоничное. '
    else:
        result += 'Недостаточно данных для подсчёта. '

    result += '<br/>Гемодинамические показатели: '

    systolic_pressure_centile = get_centiles(table, 'Сист. артериальное давление', systolic_pressure)
    diastolic_pressure_centile = get_centiles(table, 'Диаст. артериальное давление', diastolic_pressure)
    heart_rate_centile = get_centiles(table, 'Частота сердечных сокращений', heart_rate)

    if all([systolic_pressure_centile, diastolic_pressure_centile, heart_rate_centile]):
        if 2 <= systolic_pressure_centile <= 7 and 2 <= diastolic_pressure_centile <= 7 and 2 <= heart_rate_centile <= 7:
            result += 'Гармоничное.'
        else:
            result += 'Дисгармоничное.'
    else:
        result += 'Недостаточно данных для подсчёта.'

    return result



# @eel.expose
# def convert_value_py(last_name, first_name, dad_name, dob, doi):
#     return save_common_info(last_name, first_name, dad_name, dob, doi)


def determine_the_passport_age(dob, doi):
    age = relativedelta(doi, dob)
    # print(age)
    return age


def choose_table(age, gender):
    if gender == "М":
        first = "Мальчики"
    else:
        first = "Девочки"

    # массив временных меток, между которыми меняется возраст
    years_steps = [[2,10,16],[3,2,29],[3,3,0],[3,8,29],[3,9,0],[4,2,29],[4,3,0],[4,8,29],[4,9,0],[5,2,29],[5,3,0],[5,8,29],[5,9,0],[6,2,29],[6,3,0],[6,8,29],[6,9,0],[7,5,29],[7,6,0],[8,5,29],[8,6,0],[9,5,29],[9,6,0],[10,5,29],[10,6,0],[11,5,29],[11,6,0],[12,5,29],[12,6,0],[13,5,29],[13,6,0],[14,5,29],[14,6,0],[15,5,29],[15,6,0],[16,5,29],[16,6,0],[17,5,29]]
    years = ["3","3,5","4","4,5","5","5,5","6","6,5","7","8","9","10","11","12","13","14","15","16","17"]  # массив возможных значений для имени таблицы (па размеру совпадает с предыдущим массивом)

    second = None
    third = None
    converted_age = age.years*10000 + age.months*100 + age.days  # для кодировки в формате yymmdd

    for i in range(0, len(years_steps), 2):
        left_border = years_steps[i][0]*10000 + years_steps[i][1]*100 + years_steps[i][2]
        right_border = years_steps[i+1][0]*10000 + years_steps[i+1][1]*100 + years_steps[i+1][2]
        if left_border <= converted_age <= right_border:
            second = years[int(i/2)]
            if left_border >= 40900:  # перешли порог с года до лет (см названия таблиц после 4,5 года)
                third = "лет"
            else:
                third = "года"
            break

    if second is None:  # если возраст не попал в границы, то кидаем exception
        raise RuntimeError('bad age')

    return metadata.tables[f"{first}, {second} {third}"]


def get_centiles(table, col_name, value):
    all_rows = table.select().execute().fetchall()
    for num, row in enumerate(all_rows):
        try:
            if row[col_name] > int(value):
                return num + 1
        except NoSuchColumnError:
            return 0

    return 8
