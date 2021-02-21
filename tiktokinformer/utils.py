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
