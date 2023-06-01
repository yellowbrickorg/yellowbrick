from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .views import BrickListView, BrickDetailView, SetDetailView

urlpatterns = [
    # /
    path("", views.index, name="index"),
    # /collection/
    path("collection/", views.collection, name="collection"),
    # /filter/
    path("filter/", views.filter_collection, name="filter"),
    # /collection/
    path("collection", views.collection, name="collection"),

    # /collection/o<> - owned sets management
    path("collection/o<int:owned_id>", views.owned_set,
         name="owned_set"),
    path("collection/o<int:owned_id>/missing", views.mark_missing,
         name="mark_missing"),
    path("collection/o<int:owned_id>/found", views.mark_found,
         name="mark_found"),
    path("collection/<int:legoset_id>/convert", views.set_convert_to_owned,
         name="set_convert_to_owned"),
    path("collection/o<int:owned_id>/convert", views.owned_convert_back,
         name="owned_convert_back"),

    path("wishlist", views.wishlist, name="wishlist"),
    # /bricks/
    path("bricks/", BrickListView.as_view(), name="brick_list"),
    path("bricks/<int:pk>/", BrickDetailView.as_view(), name="brick_detail"),
    path("bricks/add/<int:brick_id>", views.add_brick, name="add_brick"),
    path("bricks/del/<int:brick_id>", views.del_brick, name="del_brick"),
    path(
        "bricks/del_brick_from_wishlist/<int:brick_id>/<int:side>",
        views.del_brick_from_wishlist,
        name="del_brick_from_wishlist",
    ),
    path("get_brick_image/", views.get_brick_image, name="get_brick_image"),
    # /sets/
    path("sets_to_build/", views.sets_to_build, name="sets_to_build"),
    path("add_custom_lego_set/", views.add_custom_lego_set, name="add_custom_lego_set"),
    path(
        "edit_lego_set/<int:lego_set_id>/",
        views.edit_custom_lego_set,
        name="edit_lego_set",
    ),
    path(
        "delete_custom_lego_set/<int:pk>/",
        views.delete_custom_lego_set,
        name="delete_custom_lego_set",
    ),
    path(
        "unhide_lego_set/<int:pk>/",
        views.unhide_custom_lego_set,
        name="unhide_lego_set",
    ),
    path("sets/", views.legoset_list, name="sets"),
    path("sets/filter/", views.legoset_list, name="legoset_list_filtered"),
    path("sets/<int:pk>/", SetDetailView.as_view(), name="set_detail"),
    path("filter/run", views.filter_collection, name="filter_run"),
    path(
        "set/add_brick_to_wishlist/<int:id>/<int:side>",
        views.add_brick_to_wishlist,
        name="add_brick_to_wishlist",
    ),
    path("set/add/<int:id>/", views.add_set, name="add_set"),
    path("set/build/<int:id>/", views.build_set, name="build_set"),
    path(
        "set/add_set_to_wishlist/<int:id>/<int:side>",
        views.add_set_to_wishlist,
        name="add_set_to_wishlist",
    ),
    path(
        "set/del_set_from_wishlist/<int:id>/<int:side>",
        views.del_set_from_wishlist,
        name="del_set_from_wishlist",
    ),
    path("set/build/<int:id>", views.build_set, name="build_set"),
    path("set/dismantle/<int:id>", views.dismantle_set, name="dismantle_set"),
    path("set/del/<int:id>", views.del_set, name="del_set"),
    path("set/convert/<int:id>", views.convert, name="convert"),
    path("set/add_review/<int:id>", views.add_review, name="add_review"),
    path("set/del_review/<int:id>", views.del_review, name="del_review"),
    # Account management
    path("auth/login/", views.login, name="login"),
    path("auth/signup/", views.signup, name="signup"),
    path("auth/password_reset/", views.password_reset, name="password_reset"),
    path("auth/logout/", views.logout, name="logout"),
    path(
        "auth/reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_newpass.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "auth/reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_sent.html"
        ),
        name="password_reset_complete",
    ),
    # Exchange
    path("exchange/", views.exchange, name="exchange"),
    path("exchange/make_offer", views.exchange_make_offer, name="exchange_make_offer"),
    path("exchange/offers", views.exchange_offers, name="exchange_offers"),
    path(
        "exchange/continue_exchange",
        views.exchange_offer_continue,
        name="exchange_offer_continue",
    ),
    path("exchange/delete", views.exchange_delete_offer, name="delete_offer"),
    path("exchange/offer_details", views.offer_details, name="offer_details"),
    path("exchange/counteroffer", views.counteroffer_continue, name="counteroffer_continue"),
]
