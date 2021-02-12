from django.db import models

from wagtail.core.models import Page, Orderable
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index

# ツリー構造の中で、幹というか茎？の部分(node)
class BlogIndexPage(Page):
    intro = RichTextField(blank=True)

    # content_panels = Page.content_panels + [
    #     FieldPanel('intro', classname="full")
    # ]
    def get_context(self, request):
        # Update context to include only published posts, ordered by reverse-chron
        context = super().get_context(request)
        blogpages = self.get_children().live().order_by('-first_published_at') # live()で、publishされているものだけ表示
        context['blogpages'] = blogpages
        return context

# ツリー構造の中で、葉の部分
class BlogPage(Page):
    date = models.DateField("Post date")
    intro = models.CharField(max_length=250)
    body = RichTextField(blank=True)

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('intro'),
        FieldPanel('body', classname="full"),
    ]

"""Doc Page Models"""
# class BlogPage(Page):
#     # Database fields
#     body = RichTextField()
#     date = models.DateField("Post date")
#     feed_image = models.ForeignKey(
#         'wagtailimages.Image',
#         null=True,
#         blank=True,
#         on_delete=models.SET_NULL,
#         related_name='+'
#     )

#     # Search index configuration
#     search_fields = Page.search_fields + [
#         index.SearchField('body'),
#         index.FilterField('date'),
#     ]

#     # Editor panels configuration
#     content_panels = Page.content_panels + [
#         FieldPanel('date'),
#         FieldPanel('body', classname="full"),
#         InlinePanel('related_links', label="Related links"),
#     ]

#     promote_panels = [
#         MultiFieldPanel(Page.promote_panels, "common page configuration"),
#         ImageChooserPanel('feed_image')
#     ]

#     # Parent page / subpage type rules

#     parent_page_types = ['blog.BlogIndex']
#     subpage_types = []

# class BlogPageRelatedLink(Orderable):
#     page = ParentalKey(BlogPage, on_delete=models.CASCADE, related_name='related_links')
#     name = models.CharField(max_length=255)
#     url = models.URLField()

#     panels = [
#         FieldPanel('name'),
#         FieldPanel('url'),
#     ]
