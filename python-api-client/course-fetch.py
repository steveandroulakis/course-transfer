import logging
from datetime import timedelta
from time import gmtime, strftime

import mysql.connector
import requests
import requests_cache
from simplejson import JSONDecodeError

MYSQL_DATABASE = 'ct'
MYSQL_HOSTNAME = 'localhosst'
MYSQL_PASSWORD = 'CHANGEME!!!'
MYSQL_USERNAME = 'CHANGEME!!!'
HACKAMON_CLIENT_SECRET = 'CHANGEME!!!'
HACKAMON_CLIENT_ID = 'CHANGEME!!!'

BASE_URL = 'https://mix-dev.monash.edu/hackamon2016'

logger = logging.getLogger(__name__)

expire_after = timedelta(hours=0.5)
requests_cache.install_cache('hackamon_cache', expire_after=expire_after)


class HackaMonAPI(object):
    def __init__(self, client_id, client_secret):
        self.headers = {
            'client_id': client_id,
            'client_secret': client_secret
        }

    def _do_request(self, resource, parameters, is_post=False):
        """
        Initiates a request with the Hackamon API
        :param parameters: parameters to be included in the request
        :param is_post: True if the request is by POST, or False if GET
        :return: an object containing the JSON values returned
        """

        url = '/'.join([BASE_URL, resource])
        if is_post:
            result = requests.post(url, data=parameters, headers=self.headers)
        else:
            result = requests.get(url, params=parameters, headers=self.headers)

        try:
            result_json = result.json()
        except JSONDecodeError:
            logger.debug(result.text)
            raise

        logger.debug("Requesting resource: %s" % url)
        logger.debug("Result: %s" % result_json)

        result.raise_for_status()

        return result_json

    def get_courses(self):
        query_result = self._do_request('learning-and-teaching/courses', {})
        course_list = query_result['_embedded']['courses']

        result = []
        for course in course_list:
            result.append({
                'code': course['code'],
                'title': course['title'],
                'offerings': course['_embedded']['courseOfferingPatterns'],
                'specialisations': course['_embedded']['specialisations'],
                'faculty': course['_embedded']['faculty']['description']
            })

        return result


api = HackaMonAPI(HACKAMON_CLIENT_ID,
                  HACKAMON_CLIENT_SECRET)

cnx = mysql.connector.connect(user=MYSQL_USERNAME, password=MYSQL_PASSWORD,
                              host=MYSQL_HOSTNAME,
                              database=MYSQL_DATABASE)

cursor = cnx.cursor()

now = strftime("%Y-%m-%d %H:%M:%S", gmtime())
for course in api.get_courses():
    for specialisation in course['specialisations']:
        specialisation_name = specialisation['title']
        specialisation_exists_query = 'SELECT COUNT(*) FROM `fabrik_specialisations` WHERE `course_code` = %s AND `name` = %s'
        cursor.execute(specialisation_exists_query,
                       (course['code'], specialisation_name))
        # Skip specialisation, already exists
        if cursor.fetchone()[0] > 0:
            continue

        specialisation_query = '''
INSERT INTO `fabrik_specialisations`
(`date_time`, `course_code`, `name`, `status`) VALUES (%s, %s, %s, 'CLOSED');
'''
        cursor.execute(specialisation_query, (
            now,
            course['code'],
            specialisation_name
        ))

    for offering in course['offerings']:
        location = offering['location'] or ''
        mode = offering['attendanceMode'] or ''

        location_mode_exists_query = 'SELECT COUNT(*) FROM `fabrik_location_mode` WHERE location = %s AND mode = %s AND course_code = %s'
        cursor.execute(location_mode_exists_query,
                       (location, mode, course['code']))
        if cursor.fetchone()[0] == 0:
            location_mode_query = ''' INSERT INTO `fabrik_location_mode` (`date_time`, `location`, `mode`, `course_code`, `status`) VALUES (%s, %s, %s, %s, 'CLOSED')'''
            cursor.execute(location_mode_query,
                           (now, location, mode, course['code']))

        course_exists_query = 'SELECT COUNT(*) FROM `fabrik_courses` WHERE `course_code` = %s'
        cursor.execute(course_exists_query, (course['code'],))
        # Skip course, already exists
        if cursor.fetchone()[0] > 0:
            continue

        course_query = '''
INSERT INTO `fabrik_courses`
(`date_time`,
`course_status`,
`course_code`,
`course_title`,
`managing_faculty`
) VALUES (%s, 'CLOSED', %s, %s, %s);'''
        course_query_data = (
            now,
            course['code'],
            course['title'],
            course['faculty']
        )

        cursor.execute(course_query, course_query_data)

cnx.close()
