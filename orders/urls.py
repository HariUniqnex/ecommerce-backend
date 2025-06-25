from django.urls import path
from .views import OrderList, OrderDetailView, AmazonOrderSyncView, DashboardStatsView
from django.views.generic import TemplateView

urlpatterns = [
    path('orders/sync/', AmazonOrderSyncView.as_view()),     
    path('orders/', OrderList.as_view()),
    path('orders/<str:order_id>/', OrderDetailView.as_view()),
    path('orders/stats', DashboardStatsView.as_view()),

    path('', TemplateView.as_view(template_name='index.html')),
]
