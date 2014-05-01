import unittest2 as unittest
from plone.testing import z2
from plone.app.testing.interfaces import SITE_OWNER_NAME
from plone.app.testing import login
from Products.CMFCore.utils import getToolByName

from ploneintranet.workspace.testing import \
    PLONEINTRANET_WORKSPACE_INTEGRATION_TESTING


class BaseTestCase(unittest.TestCase):

    layer = PLONEINTRANET_WORKSPACE_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.qi_tool = getToolByName(self.portal, 'portal_quickinstaller')
        self.request = self.portal.REQUEST

    def login(self, username):
        login(self.portal, username)

    def login_as_portal_owner(self):
        z2.login(self.app['acl_users'], SITE_OWNER_NAME)

    def login_as(self, username):
        """
        helper method to login as specific user
        """
        z2.login(self.portal['acl_users'], username)

    def logout(self):
        z2.logout()
