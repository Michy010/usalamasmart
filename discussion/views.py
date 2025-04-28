from django.shortcuts import render, redirect
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Topic, Reply
from django.core.paginator import Paginator

@login_required
def discussion_home(request):
    topic_list = Topic.objects.all().order_by('-created_at')
    paginator = Paginator(topic_list, 5)
    page_number = request.GET.get('page')
    page_object = paginator.get_page(page_number)

    context = {
        'topics':page_object
    }
    return render (request, 'discussion/discussion_home.html', context)

@login_required(login_url='/accounts/signin/')
def create_topic(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        Topic.objects.create(title=title, content=content, user=request.user)
        return redirect('discussion:discussion-page')
    return render(request, 'discussion/create_topic.html')


# Display the topic with its replies
@login_required
def topic_detail(request, pk):
    topic = get_object_or_404(Topic, pk=pk)
    replies = Reply.objects.filter(topic=topic, parent=None).order_by('created_at')
    return render(request, 'discussion/topic_detail.html', {
        'topic': topic,
        'replies': replies
    })

# Handle AJAX reply submissions (main and nested replies)
@login_required
def ajax_add_reply(request, topic_pk, parent_pk=None):
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if not content:
            return JsonResponse({'status': 'error', 'message': 'Reply cannot be empty'}, status=400)

        topic = get_object_or_404(Topic, pk=topic_pk)
        parent = get_object_or_404(Reply, pk=parent_pk) if parent_pk else None

        reply = Reply.objects.create(
            topic=topic,
            parent=parent,
            user=request.user,
            content=content,
            created_at=timezone.now()
        )

        return JsonResponse({
            'status': 'success',
            'reply': {
                'id': reply.id,
                'user': reply.user.username,
                'content': reply.content,
                'created_at': reply.created_at.strftime('%d %b %Y %H:%M'),
                'parent_id': parent.id if parent else None
            }
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
