from django.shortcuts import redirect

class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            return redirect('login')  # Điều hướng về trang đăng nhập nếu người dùng chưa đăng nhập
        response = self.get_response(request)
        return response