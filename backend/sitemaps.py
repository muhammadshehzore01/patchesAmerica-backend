# #project/backend/sitemap.py
# from django.contrib.sitemaps import Sitemap
# from api.models import Service, BlogPost  # your models

# class ServiceSitemap(Sitemap):
#     changefreq = "weekly"
#     priority = 0.8

#     def items(self):
#         return Service.objects.all()

#     def lastmod(self, obj):
#         return obj.updated_at  # use your model field

# class BlogSitemap(Sitemap):
#     changefreq = "weekly"
#     priority = 0.7

#     def items(self):
#         return BlogPost.objects.all()

#     def lastmod(self, obj):
#         return obj.updated_at



# class FrontendPageSitemap(Sitemap):
#     changefreq = "weekly"
#     priority = 0.9

#     def items(self):
#         return [
#             {"loc": "/", "lastmod": None},
#             {"loc": "/contact/", "lastmod": None},
#             {"loc": "/about/", "lastmod": None},
#             {"loc": "/services/", "lastmod": None},
#             {"loc": "/blog/", "lastmod": None},
#             # add more static pages if needed
            
#         ]

#     def location(self, obj):
#         return obj["loc"]