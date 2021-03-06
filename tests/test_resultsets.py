from tests import unittest, mock, Redmine, URL

response = {
    'projects': [
        {'name': 'Foo', 'identifier': 'foo', 'id': 1},
        {'name': 'Bar', 'identifier': 'bar', 'id': 2},
        {'name': 'Baz', 'identifier': 'baz', 'id': 3},
    ]
}


class TestResultSet(unittest.TestCase):
    def setUp(self):
        self.url = URL
        self.redmine = Redmine(self.url)
        self.response = mock.Mock(**{'status_code': 200, 'json.return_value': response})
        patcher = mock.patch('requests.get', return_value=self.response)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_has_custom_repr(self):
        self.assertEqual(
            repr(self.redmine.project.all()),
            '<redmine.resultsets.ResourceSet object with Project resources>'
        )

    def test_offset_limit(self):
        self.response.json.return_value = {'projects': response['projects'][1:3]}
        projects = self.redmine.project.all()[1:3]
        self.assertEqual(projects.limit, 3)
        self.assertEqual(projects.offset, 1)
        self.assertEqual(projects[0].id, 2)
        self.assertEqual(projects[1].id, 3)

    def test_limit_more_than_100(self):
        self.response.json.return_value = response
        projects = self.redmine.project.all()[:200]
        self.assertEqual(projects.limit, 200)
        self.assertEqual(projects.offset, 0)
        self.assertEqual(projects[0].id, 1)
        self.assertEqual(projects[1].id, 2)
        self.assertEqual(projects[2].id, 3)

    def test_resultset_is_empty(self):
        self.response.json.return_value = None
        projects = self.redmine.project.all()
        self.assertEqual(len(projects), 0)
        self.assertEqual(list(projects), [])

    def test_sliced_resultset_is_empty(self):
        self.response.json.return_value = None
        projects = self.redmine.project.all()[:200]
        self.assertEqual(len(projects), 0)
        self.assertEqual(list(projects), [])

    def test_supports_iteration(self):
        projects = list(self.redmine.project.all())
        self.assertEqual(projects[0].name, 'Foo')
        self.assertEqual(projects[0].identifier, 'foo')
        self.assertEqual(projects[0].id, 1)
        self.assertEqual(projects[1].name, 'Bar')
        self.assertEqual(projects[1].identifier, 'bar')
        self.assertEqual(projects[1].id, 2)

    def test_supports_len(self):
        self.assertEqual(len(self.redmine.project.all()), 3)

    def test_get_method_resource_found(self):
        projects = self.redmine.project.all().get(2)
        self.assertEqual(projects.id, 2)

    def test_get_method_resource_not_found(self):
        projects = self.redmine.project.all().get(6)
        self.assertEqual(projects, None)

    def test_filter_method(self):
        projects = self.redmine.project.all().filter((1, 3))
        self.assertEqual(projects[0].id, 1)
        self.assertEqual(projects[1].id, 3)

    def test_filter_param_exception(self):
        from redmine.exceptions import ResourceSetFilterParamError
        self.assertRaises(ResourceSetFilterParamError, lambda: self.redmine.project.all().filter(1))

    def test_index_error_exception(self):
        from redmine.exceptions import ResourceSetIndexError
        self.assertRaises(ResourceSetIndexError, lambda: self.redmine.project.all()[6])
