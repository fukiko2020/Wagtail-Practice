from django import forms
from django.db import models

from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase

from wagtail.core.models import Page, Orderable
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtail.snippets.models import register_snippet

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


class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey(
        'BlogPage',
        related_name='tagged_items',
        on_delete=models.CASCADE
    )


# ツリー構造の中で、葉の部分
class BlogPage(Page):
    date = models.DateField("Post date")
    intro = models.CharField(max_length=250)
    body = RichTextField(blank=True)
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
    categories = ParentalManyToManyField('blog.BlogCategory', blank=True)

    # ギャラリーの最初の画像を返す独自メソッド
    def main_image(self):
        gallery_item = self.gallery_images.first()
        if gallery_item:
            return gallery_item.image
        else:
            return None

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

    # 編集画面に表示されるパネル
    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('date'),
            FieldPanel('tags'),
            FieldPanel('categories', widget=forms.CheckboxSelectMultiple),
        ], heading="Blog information"),
        FieldPanel('intro'),
        FieldPanel('body'),
        # BlogPageGalleryImageのgallery_imagesをBlogPageに追加
        InlinePanel('gallery_images', label="Gallery images"),
    ]


# 画像専用のモデルを作る
# そうすれば、テンプレートの中でレイアウトやスタイルをコントロールしやすくなる
# 文字とは独立してどこでも使えるようにもなる。サムネイルなど
class BlogPageGalleryImage(Orderable):
    # Orderable:モデルにsort_orderフィールドを追加。ギャラリー内での画像の順番を追跡
    # ParentalKey:BlogPageGalleryImageをBlogPageの子モデルとして定義
    page = ParentalKey(BlogPage, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ForeignKey(
        # wagtailのImageモデルのForeignKey
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )
    caption = models.CharField(blank=True, max_length=250)

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('caption'),
    ]

# ブログ記事のタグボタンをクリックしたときの画面
class BlogTagIndexPage(Page):
    # Pageを継承しているが、フィールドは定義していない

    def get_context(self, request):

        # Filter by tag
        tag = request.GET.get('tag')
        blogpages = BlogPage.objects.filter(tags__name=tag)

        # Update template context
        context = super().get_context(request)
        context['blogpages'] = blogpages
        return context

# authorモデルとauthorのProfileが未定義(練習)

# snippets：管理画面で管理できるが、ページのツリーモデルには含まれない、再利用可能な部品
@register_snippet  # このデコレータによってモデルをsnippetとして登録
# カテゴリーはそれ自体のページを持たないので、普通のModelとして定義
class BlogCategory(models.Model):
    name = models.CharField(max_length=255)
    icon = models.ForeignKey(
        'wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+'
    )

    # snippetsの管理画面の編集画面はcontent/promote/settingに分かれていないので、content_panelとする必要はない
    panels = [
        FieldPanel('name'),
        ImageChooserPanel('icon'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'blog categories'

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
