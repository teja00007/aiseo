from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from .models import Project,Topicslist,KeywordSuggestionJob,Topic
from .serializers import ProjectSerializer,TopicslistSerializer,KeywordSuggestionJobSerializer,TopicSerializer, blogSerializer
from rest_framework import generics,status
from rest_framework.response import  Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.conf import settings
import openai
import jwt
import argparse
import sys
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

# Location IDs are listed here:
# https://developers.google.com/google-ads/api/reference/data/geotargets
# and they can also be retrieved using the GeoTargetConstantService as shown
# here: https://developers.google.com/google-ads/api/docs/targeting/location-targeting
_DEFAULT_LOCATION_IDS = ["1023191"]  # location ID for New York, NY
# A language criterion ID. For example, specify 1000 for English. For more
# information on determining this value, see the below link:
# https://developers.google.com/google-ads/api/reference/data/codes-formats#expandable-7
_DEFAULT_LANGUAGE_ID = "1000"  # language ID for English
openai.api_key = "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"

from django.contrib.auth import get_user_model
User = get_user_model()

class ProjectList(generics.GenericAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    token_param_config = openapi.Parameter(
        'token', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)
	
    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self,request, *args, **kwargs):
        token = request.GET.get('token')
        #import pdb;pdb.set_trace()
        payload = jwt.decode(token, settings.SECRET_KEY,algorithms='HS256')
        user = User.objects.get(id=payload['user_id'])
        queryset = Project.objects.filter(user=user)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(manual_parameters=[token_param_config])
    def post(self,request):
        token = request.GET.get('token')
        try:
            #import pdb;pdb.set_trace()
            payload = jwt.decode(token, settings.SECRET_KEY,algorithms='HS256')
            user = User.objects.get(id=payload['user_id'])
            data = request.data
            if user.is_verified:
                request.data['user'] = user
                Project.objects.create(**request.data)
                return Response({'status':'success'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)	
        except Exception as e:
            return  Response({'Exception':str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

class ProjectDetail(generics.GenericAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    token_param_config = openapi.Parameter(
        'token', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)
	
    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self,request, *args, **kwargs):
        project_id =  kwargs['pk']
        queryset = Project.objects.get(pk=project_id)
        serializer = self.serializer_class(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(manual_parameters=[token_param_config])
    def delete(self,request, *args, **kwargs):
        token = request.GET.get('token')
        try:
            #import pdb;pdb.set_trace()
            project_id =  kwargs['pk']
            queryset = Project.objects.filter(pk=project_id)
            queryset.delete()
            return Response({'status':'success'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)	
        except Exception as e:
            return  Response({'Exception':str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

class KeywordSuggestionJobList(generics.GenericAPIView):
    queryset = KeywordSuggestionJob.objects.all()
    serializer_class = KeywordSuggestionJobSerializer
    token_param_config = openapi.Parameter(
        'token', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)
	
    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self,request, *args, **kwargs):
        #import pdb;pdb.set_trace()
        token = request.GET.get('token')
        #import pdb;pdb.set_trace()
        payload = jwt.decode(token, settings.SECRET_KEY,algorithms='HS256')
        user = User.objects.get(id=payload['user_id'])
        if user.is_verified:
            project_id =  kwargs['project_id']
            project = Project.objects.get(id=project_id)
            queryset = KeywordSuggestionJob.objects.filter(project=project)
            serializer = self.serializer_class(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(manual_parameters=[token_param_config])
    def post(self,request, *args, **kwargs):
        token = request.GET.get('token')
        project_id =  kwargs['project_id']
        try:
            #import pdb;pdb.set_trace()
            payload = jwt.decode(token, settings.SECRET_KEY,algorithms='HS256')
            user = User.objects.get(id=payload['user_id'])
            data = request.data
            if user.is_verified:
                googleads_client = GoogleAdsClient.load_from_storage(version="v13")
                keyword_ideas = main(
                        googleads_client,
                        "1718568854",
                        _DEFAULT_LOCATION_IDS,
                        _DEFAULT_LANGUAGE_ID,
                        [str(request.data['keywords'])],
                        None
                    )
                #import pdb;pdb.set_trace()
                request.data['project'] = Project.objects.get(id=project_id)
                request.data['keyword_ideas'] = keyword_ideas
                KeywordSuggestionJob.objects.create(**request.data)
                return Response({'status':str(keyword_ideas)}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)	
        except Exception as e:
            return  Response({'Exception':str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
class KeywordSuggestionJobDetail(generics.GenericAPIView):
    queryset = KeywordSuggestionJob.objects.all()
    serializer_class = KeywordSuggestionJobSerializer
    token_param_config = openapi.Parameter(
        'token', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)
	
    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self,request, *args, **kwargs):
        #import pdb;pdb.set_trace()
        job_id =  kwargs['pk']
        queryset = KeywordSuggestionJob.objects.get(pk=job_id)
        serializer = self.serializer_class(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(manual_parameters=[token_param_config])
    def delete(self,request, *args, **kwargs):
        #import pdb;pdb.set_trace()
        job_id =  kwargs['pk']
        KeywordSuggestionJob.objects.delete(pk=job_id)
        return Response({'status':'sucess'}, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(manual_parameters=[token_param_config])
    def post(self,request, *args, **kwargs):
        #import pdb;pdb.set_trace()
        token = request.GET.get('token')
        project_id =  kwargs['pk']
        try:
            payload = jwt.decode(token, settings.SECRET_KEY,algorithms='HS256')
            user = User.objects.get(id=payload['user_id'])
            data = request.data
            if user.is_verified:
                #import pdb;pdb.set_trace()
                _list = []
                for keyword in request.data['keyword_ideas']:
                    _list.append(keyword['Keyword'])
                job = KeywordSuggestionJob.objects.get(id=project_id)
                #request.data['project'] = KeywordSuggestionJob.objects.filter(id=project_id).update(keyword_ideas = request.data['keyword_ideas'])
                prompt = "generate a list of 2 blog tiles from the keywords "+ ','.join(_list)
                topics = openai_response(prompt)
                topics_split = topics.strip().split('\n')
                topics = [top.split('.')[1].strip() for top in topics_split]
                for topic in topics:
                    topic_data = {
                        'job': job,
                        'title' : topic,
                        'selected': True
                    }
                    Topicslist.objects.create(**topic_data)
                _list = Topicslist.objects.filter(job=job)
                for Tpiclist in _list:
                    #import pdb;pdb.set_trace()
                    prompt = Tpiclist.title
                    project = Tpiclist.job.project.id
                    data = blog_generator.delay(prompt,project,Tpiclist.id)
                return Response({'status':'success'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)	
        except Exception as e:
            return  Response({'Exception':str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

class TopicList(generics.GenericAPIView):
    queryset = Topicslist.objects.all()
    serializer_class = TopicslistSerializer
    token_param_config = openapi.Parameter(
        'token', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)
    
    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self,request, *args, **kwargs):
        #import pdb;pdb.set_trace()
        token = request.GET.get('token')
        #import pdb;pdb.set_trace()
        payload = jwt.decode(token, settings.SECRET_KEY,algorithms='HS256')
        user = User.objects.get(id=payload['user_id'])
        if user.is_verified:
            job_id =  kwargs['job_id']
            job = KeywordSuggestionJob.objects.get(pk=job_id)
            queryset = Topicslist.objects.filter(job=job)
            serializer = self.serializer_class(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.data, status=status.HTTP_200_OK)

class TopicDetail(generics.GenericAPIView):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    token_param_config = openapi.Parameter(
        'token', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)
	
    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self,request, *args, **kwargs):
        #import pdb;pdb.set_trace()
        topic_id =  kwargs['Topic_id']
        Tpiclist = Topicslist.objects.get(pk=topic_id)
        queryset = Topic.objects.filter(topic=Tpiclist)
        if queryset:
            serializer = self.serializer_class(queryset[0])
            data = serializer.data
        else:
            # prompt = Tpiclist.title
            # project = Tpiclist.job.project
            # data_dict = blog_generator(prompt,project,Tpiclist)
            # #import pdb;pdb.set_trace()
            # serializer = self.serializer_class(data_dict[0])
            # data = serializer.data
            data = {"status":"blog not generated yet"}
        return Response(data, status=status.HTTP_200_OK)

    # @swagger_auto_schema(manual_parameters=[token_param_config])
    # def delete(self,request, *args, **kwargs):
    #     #import pdb;pdb.set_trace()
    #     job_id =  kwargs['pk']
    #     Topicslist.objects.delete(pk=job_id)
    #     return Response({'status':'success'},status=status.HTTP_200_OK)
    
    # @swagger_auto_schema(manual_parameters=[token_param_config])
    # def post(self,request, *args, **kwargs):
    #     job_id =  kwargs['pk']
    #     queryset = Topicslist.objects.delete(pk=job_id)
    #     return Response({'status':'success'},status=status.HTTP_200_OK)

class wordpress_push(generics.GenericAPIView):
    queryset = Topic.objects.all()
    serializer_class = blogSerializer
    token_param_config = openapi.Parameter(
        'token', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)
	
    # @swagger_auto_schema(manual_parameters=[token_param_config])
    # def get(self,request, *args, **kwargs):
    #     #import pdb;pdb.set_trace()
    #     topic_id =  kwargs['Topic_id']
    #     image_url =  kwargs['url']
    #     Tpiclist = Topicslist.objects.get(pk=topic_id)
    #     queryset = Topic.objects.filter(topic=Tpiclist)
    #     if queryset:
    #         data = wordpress_publish(queryset[0],image_url)
    #         return Response(data, status=status.HTTP_200_OK)

    @swagger_auto_schema(manual_parameters=[token_param_config])
    def post(self,request, *args, **kwargs):
        #import pdb;pdb.set_trace()
        data1 = request.data
        topic_id =  data1['topic_id']
        image_url =  data1['url']
        Tpiclist = Topicslist.objects.get(pk=topic_id)
        queryset = Topic.objects.filter(topic=Tpiclist)
        if queryset:
            data = wordpress_publish(queryset[0],image_url)
            return Response(data, status=status.HTTP_200_OK)



# [START generate_keyword_ideas]
def main(
    client, customer_id, location_ids, language_id, keyword_texts, page_url
):
    #import pdb;pdb.set_trace()
    keyword_plan_idea_service = client.get_service("KeywordPlanIdeaService")
    keyword_competition_level_enum = (
        client.enums.KeywordPlanCompetitionLevelEnum
    )
    keyword_plan_network = (
        client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH_AND_PARTNERS
    )
    location_rns = map_locations_ids_to_resource_names(client, location_ids)
    language_rn = client.get_service("GoogleAdsService").language_constant_path(
        language_id
    )

    # Either keywords or a page_url are required to generate keyword ideas
    # so this raises an error if neither are provided.
    if not (keyword_texts or page_url):
        raise ValueError(
            "At least one of keywords or page URL is required, "
            "but neither was specified."
        )

    # Only one of the fields "url_seed", "keyword_seed", or
    # "keyword_and_url_seed" can be set on the request, depending on whether
    # keywords, a page_url or both were passed to this function.
    request = client.get_type("GenerateKeywordIdeasRequest")
    request.customer_id = customer_id
    request.language = language_rn
    request.geo_target_constants = location_rns
    request.include_adult_keywords = False
    request.keyword_plan_network = keyword_plan_network

    # To generate keyword ideas with only a page_url and no keywords we need
    # to initialize a UrlSeed object with the page_url as the "url" field.
    if not keyword_texts and page_url:
        request.url_seed.url = page_url

    # To generate keyword ideas with only a list of keywords and no page_url
    # we need to initialize a KeywordSeed object and set the "keywords" field
    # to be a list of StringValue objects.
    if keyword_texts and not page_url:
        request.keyword_seed.keywords.extend(keyword_texts)

    # To generate keyword ideas using both a list of keywords and a page_url we
    # need to initialize a KeywordAndUrlSeed object, setting both the "url" and
    # "keywords" fields.
    if keyword_texts and page_url:
        request.keyword_and_url_seed.url = page_url
        request.keyword_and_url_seed.keywords.extend(keyword_texts)

    keyword_ideas = keyword_plan_idea_service.generate_keyword_ideas(
        request=request
    )
    data =[]
    #f=open("file.csv",'a')
    for idea in keyword_ideas:
        competition_value = idea.keyword_idea_metrics.competition.name
        print(
            f'Keyword idea text "{idea.text}" has '
            f'"{idea.keyword_idea_metrics.avg_monthly_searches}" '
            f'average monthly searches and "{competition_value}" '
            "competition.\n"
        )
        d = {
            'Keyword': idea.text,
            'Traffic': str(idea.keyword_idea_metrics.avg_monthly_searches),
            'competition_value' : competition_value
        }
        data.append(d)
        #f.write(idea.text+','+str(idea.keyword_idea_metrics.avg_monthly_searches)+','+competition_value)
        ##f.write('\n')
    #f.close()
    return data
    # [END generate_keyword_ideas]

def map_locations_ids_to_resource_names(client, location_ids):
    """Converts a list of location IDs to resource names.

    Args:
        client: an initialized GoogleAdsClient instance.
        location_ids: a list of location ID strings.

    Returns:
        a list of resource name strings using the given location IDs.
    """
    build_resource_name = client.get_service(
        "GeoTargetConstantService"
    ).geo_target_constant_path
    return [build_resource_name(location_id) for location_id in location_ids]

def openai_response(prompt):
    response = openai.Completion.create(model="text-davinci-003", prompt=prompt, temperature=0, max_tokens=800)
    #import pdb;pdb.set_trace()
    return response['choices'][0]['text']


class promptgenerator:

    def __init__(self,USERNAME,AI_NAME) -> None:
        self.conversation_history =  "INITIAL_PROMPT" + "\n"
        self.USERNAME = USERNAME
        self.AI_NAME = AI_NAME

    def handle_input(self,input_str):
        """Updates the conversation history and generates a response using GPT-3."""
        # Update the conversation history
        self.conversation_history += f"{self.USERNAME}: {input_str}\n"
    
        # Generate a response using GPT-3
        message = self.response(self.conversation_history)

        # Update the conversation history
        self.conversation_history += f"{self.AI_NAME}: {message}\n"

        # Print the response
        #print(f'{self.AI_NAME}: {message}')
        
        return message
           
    def readprompt(self):
        with open('prompts.json','r') as f:
            data = f.read()
        return eval(data)

    def response(self,prompt):
        response = openai.Completion.create(model="text-davinci-003", prompt=prompt, temperature=0, max_tokens=800)
        #import pdb;pdb.set_trace()
        return response['choices'][0]['text']

    def generate_blog(self,prompt):
        data = self.readprompt()
        data = data['Blog']
        prompt_full = data+prompt
        text = self.handle_input(prompt_full)
        return text

    def generate_blog_titles(self,prompt):
        data = self.readprompt()
        data = data['Blog Titles']
        prompt_full = data+prompt
        text = self.handle_input(prompt_full)
        return text

    def generate_related_topics(self,prompt):
        data = self.readprompt()
        data = data['Related Topics']
        prompt_full = data
        text = self.handle_input(prompt_full)
        return text

    def generate_meta_description(self,prompt):
        data = self.readprompt()
        data = data['Meta Description']
        prompt_full = data
        text = self.handle_input(prompt_full)
        return text

    def generate_excerpt(self,prompt):
        data = self.readprompt()
        data = data['Excerpt']
        prompt_full = data
        text = self.handle_input(prompt_full)
        return text

    def generate_microblogs(self,prompt):
        data = self.readprompt()
        data = data['Microblogs']
        prompt_full = data
        text = self.handle_input(prompt_full)
        return text

    def generate_keywords(self,prompt):
        data = self.readprompt()
        data = data['Keywords']
        prompt_full = data
        text = self.handle_input(prompt_full)
        return text

    def generate_hashtags(self,prompt):
        data = self.readprompt()
        data = data['hashtags']
        prompt_full = data
        text = self.handle_input(prompt_full)
        return text

from celery import Celery
from celery.utils.log import get_task_logger
from celery import shared_task
app = Celery('aiseo',broker="amqp://guest:guest@localhost:5672")
logger = get_task_logger(__name__)

@app.task
def blog_generator(prompt,project,Tpiclist):
    output = []
    USERNAME = "USER"
    AI_NAME = "AI"
    try:
        #import pdb;pdb.set_trace()
        prompt = prompt
        promptgeneratorclass = promptgenerator(USERNAME,AI_NAME)
    
        data = {
            "topic" : Topicslist.objects.get(id=Tpiclist),
            "blog": promptgeneratorclass.generate_blog(prompt),
            "blog_titles": promptgeneratorclass.generate_blog_titles(prompt),
            "related_topics": promptgeneratorclass.generate_related_topics(prompt),
            "meta_description": promptgeneratorclass.generate_meta_description(prompt),
            "excerpt": promptgeneratorclass.generate_excerpt(prompt),
            "microblogs": promptgeneratorclass.generate_microblogs(prompt),
            "keywords": promptgeneratorclass.generate_keywords(prompt),
            "hashtags": promptgeneratorclass.generate_hashtags(prompt),
            "project": Project.objects.get(id=project)
        }
        print(data)
        output.append(data)
        Topic.objects.create(**data)
        data['topic'] = Tpiclist
        data['project'] = project
        return [data]
    except Exception as e:
        print(str(e))
    
import requests
import os

def wordpress_publish(blog,image_url):
    # Set up API endpoint and authentication
    endpoint = 'http://localhost/?rest_route=/wp/v2/posts'
    username = 'teja'
    #AUTH_PASSWORD = 'teja1234!'
    password = 'URDR KVGG TZTa v0pg eY5E kHI5'

    # Create a dictionary of post data
    post_data = {
        'title': blog.topic.title,
        'content': blog.blog,
        'status': 'publish'
    }

    # # Upload an image and get the attachment ID
    # image_path = '/Users/ramtejakumarreddychintham/Desktop/work/workspace/sso_test/aiseo/project_api/test.webp'
    # headers = {'Content-Type': 'image/png'}
    # with open(image_path, 'rb') as image_file:
    #     fileName = os.path.basename(image_path)
    #     response = requests.post(url='http://localhost/?rest_route=/wp/v2/media',
    #                         data=image_file,
    #                         headers={ 'Content-Type': 'image/webp','Content-Disposition' : 'attachment; filename=%s'% fileName},
    #                         auth=(username, password))
    #import pdb;pdb.set_trace()
    import requests
    contents = requests.get(image_url).content
    #data = base64.b64encode(contents)
    import uuid
    filename = str(uuid.uuid4())+'.png'
    response = requests.post(url='http://localhost/?rest_route=/wp/v2/media',
                            data=contents,
                            headers={ 'Content-Type': 'image/png','Content-Disposition' : 'attachment; filename=%s'% filename},
                            auth=(username, password))
    print(response.text)
    attachment_id = response.json()['id']

    # Set the featured image for the post
    post_data['featured_media'] = attachment_id
    post_data['media'] = attachment_id

    # Create the post
    response = requests.post(endpoint,
                            auth=(username, password),
                            json=post_data)
    return response.json()