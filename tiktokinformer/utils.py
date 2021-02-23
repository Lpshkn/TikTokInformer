import requests
from bs4 import BeautifulSoup


def get_top_users(count: int) -> list:
    """
    Function returns names of the first $count TikTok profiles sorted by the count of subscribers

    :param count: the count of top profiles
    :return: list of names
    """
    names = []
    # Count of users on each page
    count_on_page = 100

    # Get count of pages
    page = (count - 1) // count_on_page + 1
    for page in range(1, page+1):
        # The ref to the service
        ref = 'https://www.t30p.ru/TikTok.aspx?p={}&order=0'

        response = requests.get(ref.format(page))
        if response.status_code != 200:
            raise requests.ConnectionError('Getting response from the site was failed')

        bs = BeautifulSoup(response.text, features='html.parser')
        for profile in bs.find_all('td', class_='name'):
            if len(names) == count:
                return names
            names.append(profile.find('a').get('name'))
    return names


def get_sublists(main_list: list, count: int):
    """
    Function splits the main list to $count sublists: extra elements will be appended into the first sublists.

    :param main_list: a list that will be split
    :param count: count of sublists
    :return: list of sublists
    """
    # Minimal count of elements per sublist
    count_per_list = len(main_list) // count

    # If count of elements more or equal count of sublists
    if count_per_list != 0:
        # Split the main list to 2 parts
        rest_list = main_list[count * count_per_list:]
        main_list = main_list[:count * count_per_list]

        sublists = [main_list[x:x + count_per_list] for x in range(0, len(main_list), count_per_list)]

        # Append extra elements into the first sublists
        for index, element in enumerate(rest_list):
            sublists[index].append(element)
    # If count of elements less than count of sublists
    else:
        sublists = [main_list[x:x + 1] for x in range(0, len(main_list))]

    return sublists
