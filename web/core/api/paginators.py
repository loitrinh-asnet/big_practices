"""Implementing your own paginator."""
from tastypie.paginator import Paginator


class PageNumberPaginator(Paginator):
    """Adding a page number to the output."""

    def page(self):
        """The place to implementing the page-related calculations."""
        output = super(PageNumberPaginator, self).page()
        output['page_number'] = self.offset // self.limit + 1
        return output


class EntryPaginator(Paginator):
    """Adding some fields to the output."""

    def page(self):
        """The place to implementing the page-related calculations."""
        output = super(EntryPaginator, self).page()

        # First keep a reference
        output['pagination'] = output['meta']

        # Now delete all the original keys
        del output['meta']

        return output
