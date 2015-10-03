from django.conf.urls import url
from django.db.models import Max, Q
from django.http import HttpRequest
from django.views.generic import View
from yunity.api.ids import chat_id_uri_pattern, user_id_uri_pattern

from yunity.api.utils import ApiBase, model_to_json, json_request
from yunity.models.concrete import Chat as ChatModel
from yunity.models.concrete import Message as MessageModel
from yunity.models.concrete import User as UserModel


def user_to_json(user):
    return model_to_json(user, 'id')


def message_to_json(message):
    return model_to_json(message, 'sent_by', 'created_at', 'type', 'content')


def chat_to_json(chat):
    return model_to_json(chat, 'id')


def user_has_rights_to_chat(chatid, userid):
    return ChatModel.objects \
        .filter(id=chatid) \
        .filter(Q(participants=userid) | Q(administrated_by=userid)) \
        .count() != 0


class Chats(ApiBase, View):
    def get(self, request):
        """List all chats in which the currently logged in user is involved.
        The chats are in descending order of the most recent message time; this means that the first element of the
        chats list is the chat with the most recent activity.

        response_json:
            chats:
                type: list
                description: a list of {'id'} objects describing all the chats

        :type request: HttpRequest

        """
        chats = ChatModel.objects \
            .filter(participants=request.user.id) \
            .annotate(most_recent_message=Max('messages__created_at')) \
            .order_by('-most_recent_message') \
            .all()

        return self.success({'chats': [chat_to_json(_) for _ in chats]})

    @json_request(expected_keys=['participants'])
    def post(self, data, request):
        """Create a new chat involving some participants.

        request_json:
            participants:
                type: list
                required: true
                description: the list of user ids to enroll in the new chat

        response_json:
            id:
                type: integer
                description: the id of the newly created chat

        :type data: dict
        :type request: HttpRequest
        :rtype JsonResponse

        """
        participants = data['participants']
        chat = ChatModel.objects.create(participants=participants)

        return self.success({'id': chat.id})


class Chat(ApiBase, View):
    def get(self, request, chatid):
        """fetch all the information about the chat

        :type request: HttpRequest
        :type chatid: int

        """
        raise NotImplementedError


class ChatMessages(ApiBase, View):
    def get(self, request, chatid):
        """Retrieve all the messages in the chat.

        response_json:
            messages:
                type: list
                description: the ids of all the messages in the chat

        :type request: HttpRequest
        :type chatid: int

        """
        if not user_has_rights_to_chat(chatid, request.user.id):
            return self.forbidden('user does not have rights to chat')

        messages = MessageModel.objects \
            .filter(in_conversation=chatid) \
            .all()

        return self.success({'messages': [message_to_json(_) for _ in messages]})


class ChatParticipants(ApiBase, View):
    def get(self, request, chatid):
        """List all the participants in the chat.

        response_json:
            participants:
                type: list
                description: the ids of all the users in the chat

        :type request: HttpRequest
        :type chatid: int

        """
        if not user_has_rights_to_chat(chatid, request.user.id):
            return self.forbidden('user does not have rights to chat')

        participants = ChatModel.objects \
            .get(id=chatid) \
            .participants \
            .all()

        return self.success({'participants': user_to_json(_) for _ in participants})

    @json_request(expected_keys=['users'])
    def post(self, data, request, chatid):
        """Add a list of users to the chat.

        request_json:
            users:
                type: list
                required: true
                description: a list of ids of users to remove

        :type request: HttpRequest
        :type chatid: int

        """
        if not user_has_rights_to_chat(chatid, request.user.id):
            return self.forbidden('user does not have rights to chat')

        users_to_add = UserModel.objects \
            .filter(id=data['users']) \
            .all()

        ChatModel.objects \
            .get(id=chatid) \
            .participants \
            .add(users_to_add)

        return self.success()


class ChatParticipant(ApiBase, View):
    def delete(self, request, chatid, userid):
        """Remove a user from the chat.

        request_json:
            user:
                type: integer
                required: true
                description: the id of the user to remove

        :type request: HttpRequest
        :type chatid: int
        :type userid: int

        """
        if not user_has_rights_to_chat(chatid, request.user.id):
            return self.forbidden('user does not have rights to chat')

        ChatModel.objects \
            .get(id=chatid) \
            .participants \
            .filter(id=userid) \
            .delete()

        return self.success()


urlpatterns = [
    url(r'^/?$', Chats.as_view()),
    url(r'^/{chatid}/?$'.format(chatid=chat_id_uri_pattern), Chat.as_view()),
    url(r'^/{chatid}/messages/?$'.format(chatid=chat_id_uri_pattern), ChatMessages.as_view()),
    url(r'^/{chatid}/participants/?$'.format(chatid=chat_id_uri_pattern), ChatParticipants.as_view()),
    url(r'^/{chatid}/participants/{userid}/?$'.format(chatid=chat_id_uri_pattern, userid=user_id_uri_pattern), ChatParticipant.as_view()),
]
