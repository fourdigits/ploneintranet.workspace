# coding=utf-8
from plone import api
from plone.tiles.interfaces import IBasicTile
from ploneintranet.workspace.browser.sidebar import ContentItemsTile
from ploneintranet.workspace.tests.base import BaseTestCase
from zope.component import getMultiAdapter
from zope.component import provideAdapter
from zope.interface import Interface


class TestSidebar(BaseTestCase):

    def create_workspace(self):
        """ returns adapted workspace folder"""
        workspace_folder = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace',
            title='Welcome to my workspace'
        )
        return workspace_folder
        # return IWorkspace(workspace_folder)

    def test_sidebar_children(self):
        """ Create some test content and test if children method works
        """
        self.login_as_portal_owner()
        ws = self.create_workspace()
        api.content.create(
            ws,
            'Document',
            'example-document',
            title='Some example Rich Text'
        )
        api.content.create(
            ws,
            'Folder',
            'myfolder',
            title='An example Folder'
        )
        myfolder = getattr(ws, 'myfolder')
        api.content.create(
            myfolder,
            'Document',
            'example-subdocument',
            title='Some example nested Rich Text'
        )
        provideAdapter(ContentItemsTile, (Interface, Interface), IBasicTile,
                       name=u"sidebar.default")
        sidebar = getMultiAdapter((ws, ws.REQUEST), name=u"sidebar.default")
        children = sidebar.children()

        titles = [x['title'] for x in children]
        self.assertIn('Some example Rich Text',
                      titles,
                      "File with that title not found in sidebar navigation")

        urls = [x['url'] for x in children]
        self.assertIn('http://nohost/plone/example-workspace/myfolder/'
                      '@@sidebar.default#items',
                      urls,
                      "Folder with that url not found in sidebar navigation")
        classes = [x['cls'] for x in children]
        self.assertIn('item group type-folder has-no-description',
                      classes,
                      "No such Classes found in sidebar navigation")
        ids = [x['id'] for x in children]
        self.assertNotIn('example-subdocument',
                         ids,
                         "No such IDs found in sidebar navigation")

        subsidebar = getMultiAdapter((myfolder, myfolder.REQUEST),
                                     name=u"sidebar.default")
        subchildren = subsidebar.children()
        ids = [x['id'] for x in subchildren]
        self.assertIn('example-subdocument',
                      ids,
                      "No such IDs found in sidebar navigation")

        # Check if search works
        from zope.publisher.browser import TestRequest
        TR = TestRequest(form={'sidebar-search': 'Folder'})
        sidebar = getMultiAdapter((ws, TR), name=u"sidebar.default")
        children = sidebar.children()
        self.assertEqual(len(children), 1)
        self.assertTrue(children[0]['id'] == 'myfolder')

        # Assert that substr works and we find all
        TR = TestRequest(form={'sidebar-search': 'exampl'})
        sidebar = getMultiAdapter((ws, TR), name=u"sidebar.default")
        children = sidebar.children()
        self.assertEqual(len(children), 3)
