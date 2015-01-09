from five import grok
from plone.dexterity.content import Container
from plone.directives import form
from plone.namedfile.interfaces import IImageScaleTraversable


class IWorkspaceContainer(form.Schema, IImageScaleTraversable):
    """
    Marker interface for WorkspaceContainer
    """


class WorkspaceContainer(Container):
    """
    A folder to contain WorkspaceFolders
    """
    grok.implements(IWorkspaceContainer)
