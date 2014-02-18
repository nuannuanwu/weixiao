#-*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from oauth2app.models import Client, AccessToken, Code
from base64 import b64encode
from django.test.client import Client as C
def client(request, client_id):
    client = Client.objects.get(key=client_id)
    template = {
        "client":client,
        "basic_auth":"Basic %s" % b64encode(client.key + ":" + client.secret),
        "codes":Code.objects.filter(client=client).select_related(),
        "access_tokens":AccessToken.objects.filter(client=client).select_related()}
    template["error_description"] = request.GET.get("error_description")
    return render_to_response(
        'client/client.html',
        template,
        RequestContext(request))

def login(request):
    # client_id = '0c116f028ae59bf944e701f7276682'
    client = Client.objects.get(id=1)


    a = "Basic %s" % b64encode(client.key + ":" + client.secret)
    c = C(HTTP_USER_AGENT='Mozilla/5.0',HTTP_AUTHORIZATION=a)


    access_token_url = reverse('oauth2app.token.handler')
    #access_token_url = "http://pyflask.sinaapp.com/oauth2/access_token"
    params = {"client_id":client.key,"client_secret":client.secret,"grant_type":"password",
                "username":"u2","password":"123456"}
    #url1 = "http://127.0.0.1:8000/oauth2/access_token?client_id=0c116f028ae59bf944e701f7276682&client_secret=500e35e8cf17cbb92a5a88ad16831d&grant_type=password&username=u2&password=123456"

    response1 = c.get(access_token_url,params)

    import simplejson
    v = simplejson.loads(response1.content)
    token = v['access_token']
    print request

    user_show_url = reverse('api.views.users')
    params = {"bearer_token":token}
    response2 = c.get(user_show_url,params)

    url1 = "http://"+request.META['HTTP_HOST']+response1.request['PATH_INFO']+'?'+response1.request['QUERY_STRING']
    url2 = "http://"+request.META['HTTP_HOST']+response2.request['PATH_INFO']+'?'+response2.request['QUERY_STRING']




    template = {
        "client":client,
        'url1':url1,
        'url2':url2,
        'response1':response1,
        'response2':response2,

        "basic_auth":"Basic %s" % b64encode(client.key + ":" + client.secret),
        "codes":Code.objects.filter(client=client).select_related(),
        "access_tokens":AccessToken.objects.filter(client=client).select_related()}
    template["error_description"] = request.GET.get("error_description")
    return render_to_response(
        'client/login.html',
        template,
        RequestContext(request))
