# from plone import api
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ploneintranet.workspace.utils import TYPE_MAP
from ploneintranet.workspace.utils import parent_workspace
from zope.publisher.browser import BrowserView
from zope.component import getMultiAdapter
from plone import api
from collective.workspace.interfaces import IWorkspace
from plone.app.contenttypes.interfaces import IEvent
from plone.memoize.instance import memoize
from DateTime import DateTime
from Products.CMFPlone.utils import safe_unicode
from Products.CMFCore.utils import _checkPermission as checkPermission

FOLDERISH_TYPES = ['folder']


class BaseTile(BrowserView):

    index = None

    def render(self):
        return self.index()

    def __call__(self):
        return self.render()


class SidebarSettingsMembers(BaseTile):
    """ A view to serve as the member roster in the sidebar
    """

    index = ViewPageTemplateFile("templates/sidebar-settings-members.pt")

    def users(self):
        """Get current users and add in any search results.

        :returns: a list of dicts with keys
         - id
         - title
        :rtype: list
        """
        existing_users = self.existing_users()
        existing_user_ids = [x['id'] for x in existing_users]

        # Only add search results that are not already members
        sharing = getMultiAdapter((self.my_workspace(), self.request),
                                  name='sharing')
        search_results = sharing.user_search_results()
        users = existing_users + [x for x in search_results
                                  if x['id'] not in existing_user_ids]

        users.sort(key=lambda x: safe_unicode(x["title"]))
        return users

    def my_workspace(self):
        return parent_workspace(self)

    @memoize
    def existing_users(self):

        members = IWorkspace(self.my_workspace()).members
        info = []
        portal = api.portal.get()

        for userid, details in members.items():
            user = api.user.get(userid)
            if user is None:
                continue
            user = user.getUser()
            title = user.getProperty('fullname') or user.getId() or userid
            # XXX tbd, we don't know what a persons description is, yet
            description = 'Here we could have a nice status of this person'
            classes = description and 'has-description' or 'has-no-description'
            portrait = '%s/portal_memberdata/portraits/%s' % \
                       (portal.absolute_url(), userid)

            info.append(
                dict(
                    id=userid,
                    title=title,
                    description=description,
                    portrait=portrait,
                    cls=classes,
                    member=True,
                    admin='Admins' in details['groups'],
                )
            )

        return info

    def can_manage_workspace(self):
        """
        does this user have permission to manage the workspace
        """
        return checkPermission(
            "ploneintranet.workspace: Manage workspace",
            self.context,
        )


class SidebarSettingsSecurity(BaseTile):
    """ A view to serve as the security settings in the sidebar
    """

    index = ViewPageTemplateFile("templates/sidebar-settings-security.pt")


class SidebarSettingsAdvanced(BaseTile):
    """ A view to serve as the advanced config in the sidebar
    """

    index = ViewPageTemplateFile("templates/sidebar-settings-advanced.pt")


class Sidebar(BaseTile):

    """ A view to serve as a sidebar navigation for workspaces
    """

    index = ViewPageTemplateFile("templates/sidebar.pt")

    def my_workspace(self):
        return parent_workspace(self)

    # ContentItems

    def parent(self):
        if self.context.portal_type == \
                "ploneintranet.workspace.workspacefolder":
            return None
        parent = self.context.aq_parent
        return {'id': parent.getId(),
                'title': parent.Title(),
                'url': parent.absolute_url() + '/@@sidebar.default'}

    def children(self):
        """ returns a list of dicts of items in the current context
        """
        items = []
        catalog = self.context.portal_catalog
        current_path = '/'.join(self.context.getPhysicalPath())

        sidebar_search = self.request.get('sidebar-search', None)
        if sidebar_search:
            st = '%s*' % sidebar_search  # XXX plone only allows * as postfix.
            # With solr we might want to do real substr
            results = catalog.searchResults(SearchableText=st,
                                            path=current_path)
        else:
            results = self.context.getFolderContents()

        for item in results:
            # Do some checks to set the right classes for icons and candy
            desc = (
                item['Description']
                and 'has-description'
                or 'has-no-description'
            )

            content_type = TYPE_MAP.get(item['portal_type'], 'none')

            mime_type = ''  # XXX: will be needed later for grouping by mimetyp
            # typ can be user, folder, date and mime typish
            typ = 'folder'  # XXX: This needs to get dynamic later

            if content_type in FOLDERISH_TYPES:
                dpi = (
                    "source: #items; target: #items && "
                    "source: #selector-contextual-functions; "
                    "target: #selector-contextual-functions && "
                    "source: #context-title; target: #context-title && "
                    "source: #sidebar-search-form; "
                    "target: #sidebar-search-form"
                )
                url = item.getURL() + '/@@sidebar.default#items'
                content_type = 'group'
            else:
                dpi = "target: #document-body"
                url = item.getURL() + "#document-body"
                content_type = 'document'

            cls = 'item %s type-%s %s' % (content_type, typ, desc)

            items.append({
                'id': item['getId'],
                'cls': cls,
                'title': item['Title'],
                'description': item['Description'],
                'url': url,
                'type': TYPE_MAP.get(item['portal_type'], 'none'),
                'mime-type': mime_type,
                'dpi': dpi})
        return items

    def events(self):
        catalog = api.portal.get_tool("portal_catalog")
        workspace = parent_workspace(self.context)
        workspace_path = '/'.join(workspace.getPhysicalPath())
        now = DateTime()

        # Current and future events
        upcoming_events = catalog.searchResults(
            object_provides=IEvent.__identifier__,
            path=workspace_path,
            start={'query': (now), 'range': 'min'},
        )

        # Events which have finished
        older_events = catalog.searchResults(
            object_provides=IEvent.__identifier__,
            path=workspace_path,
            end={'query': (now), 'range': 'max'},
        )
        return {"upcoming": upcoming_events, "older": older_events}

