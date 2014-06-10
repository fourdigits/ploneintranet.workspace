from collective.workspace.interfaces import IHasWorkspace
from plone import api
from ploneintranet.workspace.tests.base import BaseTestCase
from zope.component import getMultiAdapter


class TestRoster(BaseTestCase):
    """
    tests for the roster tab/view
    """

    def test_roster_access(self):
        """
        test who can access the roster tab
        and that members can see users who are part of the workspace
        """
        self.login_as_portal_owner()
        api.user.create(username='wsmember', email="member@test.com")
        api.user.create(username='wsmember2', email="member2@test.com")
        workspace_folder = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace')
        self.add_user_to_workspace(
            'wsmember',
            workspace_folder)
        self.add_user_to_workspace(
            'wsmember2',
            workspace_folder)

        self.login('wsmember')
        self.assertTrue(IHasWorkspace.providedBy(workspace_folder))
        html = workspace_folder.restrictedTraverse('@@team-roster')()

        self.assertIn('wsmember', html)
        self.assertIn('wsmember2', html)


class TestEditRoster(BaseTestCase):
    """
    tests of the roster edit view
    """

    def setUp(self):
        super(TestEditRoster, self).setUp()
        self.login_as_portal_owner()
        api.user.create(username='wsadmin', email="admin@test.com")
        api.user.create(username='wsmember', email="member@test.com")
        api.user.create(username='wsmember2', email="member@test.com")
        workspace_folder = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace')
        self.add_user_to_workspace(
            'wsadmin',
            workspace_folder,
            set(['Admins']))
        self.add_user_to_workspace(
            'wsmember',
            workspace_folder)
        self.workspace = workspace_folder

    def test_index(self):
        view = getMultiAdapter(
            (self.workspace, self.request),
            name='edit-roster'
        )
        html = view.__call__()
        self.assertIn(
            'Edit roster for',
            html
        )

    def test_existing_users(self):
        view = getMultiAdapter(
            (self.workspace, self.request),
            name='edit-roster'
        )
        users = view.existing_users()
        wsadmin = {
            'id': 'wsadmin',
            'member': True,
            'admin': True,
            'title': 'wsadmin',
        }
        self.assertIn(
            wsadmin,
            users
        )

        wsmember = {
            'id': 'wsmember',
            'member': True,
            'admin': False,
            'title': 'wsmember'
        }
        self.assertIn(
            wsmember,
            users
        )

        self.assertTrue(
            'wsmember2' not in [user['id'] for user in users]
        )

    def test_users(self):
        self.request.form['search_term'] = 'wsmember2'
        view = getMultiAdapter(
            (self.workspace, self.request),
            name='edit-roster'
        )
        results = view.users()
        self.assertTrue(len(results))
        result_ids = [x['id'] for x in results]
        self.assertIn('wsmember2', result_ids)

    def test_update_users_remove_admin(self):
        """
        Remove admin role from workspace
        """
        view = getMultiAdapter(
            (self.workspace, self.request),
            name='edit-roster'
        )
        settings = [
            {
                'id': 'wsadmin',
                'member': True,
                'admin': False,
            },
            {
                'id': 'wsmember',
                'member': True,
            }
        ]

        view.update_users(settings)
        from collective.workspace.interfaces import IWorkspace
        members = IWorkspace(self.workspace).members
        self.assertIn(
            'wsadmin',
            members
        )
        self.assertNotIn(
            'Admins',
            IWorkspace(self.workspace).get('wsadmin').groups,
        )

    def test_update_users_remove_member(self):
        view = getMultiAdapter(
            (self.workspace, self.request),
            name='edit-roster'
        )
        settings = [
            {
                'id': 'wsmember',
                'member': False,
            },
        ]

        view.update_users(settings)
        from collective.workspace.interfaces import IWorkspace
        members = IWorkspace(self.workspace).members
        self.assertNotIn(
            'wsmember',
            members
        )

    def test_update_users_add_member(self):
        view = getMultiAdapter(
            (self.workspace, self.request),
            name='edit-roster'
        )
        settings = [
            {
                'id': 'wsmember2',
                'member': True,
            },
        ]

        view.update_users(settings)
        from collective.workspace.interfaces import IWorkspace
        members = IWorkspace(self.workspace).members
        self.assertIn(
            'wsmember2',
            members
        )
