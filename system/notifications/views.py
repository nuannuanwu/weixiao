# Create your views here.
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404, render, redirect
from django.template.context import RequestContext
from .utils import slug2id
from notifications.models import Notification
from django.http import HttpResponse

@login_required
def all(request):
    """
    Index page for authenticated user
    """
    result_list = Notification.objects.notify_group(request.user)
    notify_num = Notification.objects.count_notify_group(request.user)
   
    return render(request, 'notifications/list.html', {
        'notifications': result_list, 'notify_num':notify_num
    })
    actions = request.user.notifications.all()

    paginator = Paginator(actions, 16) # Show 16 notifications per page
    page = request.GET.get('p')

    try:
        action_list = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        action_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        action_list = paginator.page(paginator.num_pages)
        
    return render_to_response('notifications/list.html', {
        'member': request.user,
        'action_list': action_list,
    }, context_instance=RequestContext(request))

@login_required
def unread(request):
    return render(request, 'notifications/list.html', {
        'notifications': request.user.notifications.unread()
    })
    
@login_required
def mark_all_as_read(request):
    notifications = request.user.notifications.filter(unread=True)
    for n in notifications:
        n.mark_as_read()
    #request.user.notifications.mark_all_as_read()
    return redirect('notifications:all')

@login_required
def mark_as_read(request, slug=None):
    id = slug2id(slug)

    notification = get_object_or_404(Notification, recipient=request.user, id=id)
    notification.mark_as_read()

    next = request.REQUEST.get('next')

    if next:
        return redirect(next)

    return redirect('notifications:all')

@login_required
def reply_notify(request):
    id = request.GET.get("id", "")
    if id:
        try:
            notification = get_object_or_404(Notification, recipient=request.user, id=id)
            recipient = notification.recipient
            type_id = notification.action_object_content_type_id
            object_id = notification.action_object_object_id
            notifications = Notification.objects.filter(recipient=recipient, action_object_content_type_id=type_id,
                                                        action_object_object_id=object_id)
    
            notifications.update(unread=False)
            return redirect(notification.data['actions']['href'])
        except:
            pass
    return redirect('notifications:all')

@login_required
def hide_notice_box(request):
    notify_num = request.POST.get('notify_num',0)
    if notify_num:
        user = request.user
        request.session["notifications_count_" + str(user.id)] = notify_num
    return HttpResponse('')
        
