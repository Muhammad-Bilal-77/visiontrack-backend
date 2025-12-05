from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny


@api_view(['GET'])
@permission_classes([AllowAny])
def verify(request):
	user = request.user
	name = user.get_full_name() or user.username or user.email or ''
	email = user.email or ''
	return JsonResponse({
		"user": {
			"name": name,
			"email": email,
		}
	})
