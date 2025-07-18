from django.shortcuts import render

# Create your views here.
# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import BlogDetailsPage
from .serializers import BlogDetailsPageSerializer

class TagBlogAPIView(APIView):
    def get(self, request, slug):
        print(slug,"---------------------------------")
        posts = BlogDetailsPage.objects.live().public().filter(tags__slug=slug)
        serializer = BlogDetailsPageSerializer(posts, many=True, context={"request": request})
        return Response({"tag": slug, "posts": serializer.data})

    def post(self, request, slug):
        return Response({"message": "Invalid request method"})