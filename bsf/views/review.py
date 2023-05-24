from bsf.models import (
    LegoSet,
    BrickStats,
)
from .base import *


def add_review(request, id):
    lego_set = get_object_or_404(LegoSet, id=id)
    try:
        instruction_rating_mapping = {"Bad": 1, "Medium": 2, "Good": 3}

        rating = int(request.POST.get("set_rating", False))
        age = int(request.POST.get("set_age", False))
        time = int(float(request.POST.get("set_time", False)) * 10)
        instruction_rating = request.POST.get("instruction_rating", False)
        instruction_rating = instruction_rating_mapping.get(instruction_rating, None)
        review_text = request.POST.get("review_text", None)
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
            instruction_rating=instruction_rating,
            review_text=review_text,
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
