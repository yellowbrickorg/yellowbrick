from bsf.models import (
    LegoSet,
    BrickStats,
)
from .base import *


def add_review(request, id):
    lego_set = get_object_or_404(LegoSet, id=id)
    try:
        rating = int(request.POST.get("set_rating", False))
        age = int(request.POST.get("set_age", False))
        time = int(float(request.POST.get("set_time", False)) * 10)
    except:
        messages.error(
            request,
            f"Failed to add a review of {lego_set}",
        )
        return redirect(lego_set)
    else:
        logged_user = request.user
        BrickStats.objects.create(
            brick_set=lego_set,
            user=logged_user,
            likes=rating,
            min_recommended_age=age,
            build_time=time,
        )
        messages.success(
            request,
            f"Added review of {lego_set}.",
        )
        return redirect(lego_set)


def del_review(request, id):
    lego_set = get_object_or_404(LegoSet, id=id)
    logged_user = request.user
    BrickStats.objects.filter(brick_set=lego_set, user=logged_user).delete()
    messages.success(
        request,
        f"Deleted review of {lego_set}.",
    )
    return redirect(lego_set)
