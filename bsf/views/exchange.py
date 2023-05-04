from django.core.mail import send_mail, BadHeaderError
from django.template.loader import render_to_string

from bsf.models import (
    ExchangeOffer,
    BrickInOfferQuantity,
    SetInOfferQuantity,
    BrickInCollectionQuantity,
    SetInCollectionQuantity,
    Side,
    Wishlist,
)
from .base import *


def wishlist(request):
    logged_user = request.user
    if logged_user.is_authenticated:
        context = base_context(request)
        template = loader.get_template("bsf/wishlist.html")
        return HttpResponse(template.render(context, request))
    else:
        messages.info(request, "You need to be logged in to access collections.")
        return redirect("login")


def add_brick_to_wishlist(request, id, side):
    brick = get_object_or_404(Brick, brick_id=id)
    try:
        qty = int(request.POST.get("quantity", False))
    except:
        return redirect(request.POST.get("next", "/"))
    else:
        logged_user = request.user
        wishlist = BrickInWishlistQuantity.objects.filter(user=logged_user)
        if qty > 0:
            try:
                brick_through = wishlist.get(brick=brick, side=side)
            except:
                brick_through = BrickInWishlistQuantity(
                    user=logged_user, brick=brick, quantity=qty, side=side
                )
                brick_through.save()
            else:
                if side == Side.OFFERED:
                    collection = UserCollection.objects.get(user=logged_user)
                    bricks_in_collection = BrickInCollectionQuantity.objects.get(
                        brick=brick, collection=collection
                    )
                    if brick_through.quantity + qty > bricks_in_collection.quantity:
                        messages.error(request, "Can't offer more bricks than you have.")
                        return redirect(request.POST.get("next", "/"))
                brick_through.quantity = min(brick_through.quantity + qty, 10000)
                brick_through.save()
        if side == 0:
            messages.success(
                request,
                f"Added {qty} brick(s) with part number {brick.part_num} to "
                f"offered list.",
            )
        else:
            messages.success(
                request,
                f"Added {qty} brick(s) with part number {brick.part_num} to "
                f"wishlist.",
            )
        return redirect(request.POST.get("next", "/"))


def add_set_to_wishlist(request, id, side):
    lego_set = get_object_or_404(LegoSet, id=id)
    try:
        qty = int(request.POST.get("quantity", False))
    except:
        return redirect(request.POST.get("next", "/"))
    else:
        logged_user = request.user
        wishlist = SetInWishlistQuantity.objects.filter(user=logged_user)
        if qty > 0:
            try:
                set_through = wishlist.get(legoset=lego_set, side=side)
            except:
                set_through = SetInWishlistQuantity(
                    user=logged_user, legoset=lego_set, quantity=qty, side=side
                )
                set_through.save()
            else:
                if side == Side.OFFERED:
                    collection = UserCollection.objects.get(user=logged_user)
                    sets_in_collection = SetInCollectionQuantity.objects.get(
                        brick_set=lego_set, collection=collection
                    )
                    if set_through.quantity + qty > sets_in_collection.quantity:
                        messages.error(request, "Can't offer more sets than you have.")
                        return redirect(request.POST.get("next", "/"))
                set_through.quantity = min(set_through.quantity + qty, 100)
                set_through.save()
        if side == 0:
            messages.success(
                request,
                f"Added {qty} set(s) with set number {lego_set.id} to "
                f"offered list.",
            )
        else:
            messages.success(
                request,
                f"Added {qty} set(s) with set number {lego_set.id} to " f"wishlist.",
            )
        return redirect(request.POST.get("next", "/"))


def del_set_from_wishlist(request, id, side):
    lego_set = get_object_or_404(LegoSet, id=id)
    try:
        qty = int(request.POST.get("quantity", False))
    except:
        return redirect(request.POST.get("next", "/"))
    else:
        logged_user = request.user
        wishlist = SetInWishlistQuantity.objects.filter(user=logged_user)
        if qty > 0:
            try:
                set_through = wishlist.get(legoset=lego_set, side=side)
            except:
                return redirect(request.POST.get("next", "/"))
            else:
                if set_through.quantity <= qty:
                    set_through.delete()
                else:
                    set_through.quantity -= qty
                    set_through.save()
        if side == 0:
            messages.success(
                request,
                f"Removed {qty} set(s) with set number {lego_set.id} from "
                f"offered list.",
            )
        else:
            messages.success(
                request,
                f"Removed {qty} set(s) with set number {lego_set.id} from "
                f"wishlist.",
            )

        return redirect(request.POST.get("next", "/"))


def del_brick_from_wishlist(request, brick_id, side):
    brick = get_object_or_404(Brick, brick_id=brick_id)
    qty = int(request.POST.get("quantity", False))
    logged_user = request.user
    if qty > 0:
        wishlist = BrickInWishlistQuantity.objects.filter(user=logged_user)
        try:
            brick_through = wishlist.get(brick_id=brick_id, side=side)
        except (KeyError, BrickInCollectionQuantity.DoesNotExist):
            return redirect(request.POST.get("next", "/"))
        else:
            if brick_through.quantity <= qty:
                brick_through.delete()
            else:
                brick_through.quantity -= qty
                brick_through.save()
    if side == 0:
        messages.success(
            request,
            f"Removed {qty} brick(s) with part number {brick.part_num} from "
            f"offered list.",
        )
    else:
        messages.success(
            request,
            f"Removed {qty} brick(s) with part number {brick.part_num} from "
            f"wishlist.",
        )
    return redirect(request.POST.get("next", "/"))


def exchange(request):
    logged_user = request.user
    if not logged_user.is_authenticated:
        messages.error(request, "You need to be logged in to access brick exchange.")
        return redirect("index")

    possible_offers = generate_possible_offers(logged_user)
    context = base_context(request)
    context.update(
        {
            "possible_offers": possible_offers,
        }
    )
    return render(
        request=request,
        context=context,
        template_name="bsf/exchange.html",
    )


def exchange_make_offer(request):
    logged_user = request.user
    if not logged_user.is_authenticated:
        messages.error(request, "You need to be logged in to access brick exchange.")
        return redirect("index")
    other_user = request.POST.get("other_user")
    if other_user is None:
        return redirect("index")
    other_user = User.objects.get(username=other_user)
    possible_offers = generate_possible_offers(logged_user, other_user)

    new_offer = ExchangeOffer(offer_author=request.user, offer_receiver=other_user)

    bricks_in_offer = []
    sets_in_offer = []

    for brick in possible_offers[0]["brick_quantity_offered"]:
        """Bricks offered"""
        amount = request.POST.get("offer_brick_" + str(brick["brick"].brick_id))
        if amount == "":
            continue
        amount = int(amount)
        if amount > 0:
            bioq = BrickInOfferQuantity(
                offer=new_offer,
                brick=brick["brick"],
                quantity=amount,
                side=Side.OFFERED,
            )
            bricks_in_offer.append(bioq)

    for brick in possible_offers[0]["brick_quantity_wanted"]:
        """Bricks wanted"""
        amount = request.POST.get("want_brick_" + str(brick["brick"].brick_id))
        if amount == "":
            continue
        amount = int(amount)
        if amount > 0:
            bioq = BrickInOfferQuantity(
                offer=new_offer, brick=brick["brick"], quantity=amount, side=Side.WANTED
            )
            bricks_in_offer.append(bioq)

    for legoset in possible_offers[0]["set_quantity_offered"]:
        """Sets offered"""
        amount = request.POST.get("offer_set_" + str(legoset["legoset"].id))
        if amount == "":
            continue
        amount = int(amount)
        if amount > 0:
            sioq = SetInOfferQuantity(
                offer=new_offer,
                legoset=legoset["legoset"],
                quantity=amount,
                side=Side.OFFERED,
            )
            bricks_in_offer.append(sioq)

    for legoset in possible_offers[0]["set_quantity_wanted"]:
        """Sets wanted"""
        amount = request.POST.get("want_set_" + str(legoset["legoset"].id))
        if amount == "":
            continue
        amount = int(amount)
        if amount > 0:
            sioq = SetInOfferQuantity(
                offer=new_offer,
                legoset=legoset["legoset"],
                quantity=amount,
                side=Side.WANTED,
            )
            bricks_in_offer.append(sioq)

    if len(bricks_in_offer) + len(sets_in_offer) == 0:
        messages.error(request, "Can't submit an empty offer.")
        return redirect("exchange")

    new_offer.save()
    for bioq in bricks_in_offer:
        bioq.save()

    for sioq in sets_in_offer:
        sioq.save()

    """ Send an email notifying the other person about the new offer """
    subject = "New offer"
    email_template_name = "bsf/new_offer_notification.txt"
    c = {
        "email": other_user.email,
        "domain": "127.0.0.1:8000",
        "user": other_user,
        "author": logged_user,
        "protocol": "http",
    }
    email = render_to_string(email_template_name, c)
    try:
        send_mail(
            subject,
            email,
            "exchange@yellowbrick.com",
            [other_user.email],
            fail_silently=False,
        )
    except BadHeaderError:
        pass

    return redirect("exchange_offers")


def get_button_action_for(user, offer):
    is_author = offer.offer_author == user

    match offer.author_state, offer.receiver_state:
        case ExchangeOffer.Status.EXCHANGED, ExchangeOffer.Status.EXCHANGED:
            return None
        case ExchangeOffer.Status.ACCEPTED, ExchangeOffer.Status.PENDING:
            if is_author:
                return None
            else:
                return "Accept"
        case ExchangeOffer.Status.ACCEPTED, ExchangeOffer.Status.ACCEPTED:
            return "Exchange"
        case ExchangeOffer.Status.EXCHANGED, ExchangeOffer.Status.ACCEPTED:
            return None if is_author else "Exchange"
        case ExchangeOffer.Status.ACCEPTED, ExchangeOffer.Status.EXCHANGED:
            return None if not is_author else "Exchange"


def exchange_offers(request):
    logged_user = request.user
    if not logged_user.is_authenticated:
        messages.error(request, "You need to be logged in to access brick exchange.")
        return redirect("index")

    offers_made = ExchangeOffer.objects.filter(offer_author=logged_user)
    offers_received = ExchangeOffer.objects.filter(offer_receiver=logged_user)

    offers_made_context = []
    offers_received_context = []

    for offer in offers_made:
        offers_made_context.append(
            {
                "offer": offer,
                "offered_sets": SetInOfferQuantity.objects.filter(
                    offer=offer, side=Side.OFFERED
                ),
                "offered_bricks": BrickInOfferQuantity.objects.filter(
                    offer=offer, side=Side.OFFERED
                ),
                "wanted_sets": SetInOfferQuantity.objects.filter(
                    offer=offer, side=Side.WANTED
                ),
                "wanted_bricks": BrickInOfferQuantity.objects.filter(
                    offer=offer, side=Side.WANTED
                ),
                "button_action": get_button_action_for(logged_user, offer),
            }
        )

    for offer in offers_received:
        offers_received_context.append(
            {
                "offer": offer,
                "offered_sets": SetInOfferQuantity.objects.filter(
                    offer=offer, side=Side.OFFERED
                ),
                "offered_bricks": BrickInOfferQuantity.objects.filter(
                    offer=offer, side=Side.OFFERED
                ),
                "wanted_sets": SetInOfferQuantity.objects.filter(
                    offer=offer, side=Side.WANTED
                ),
                "wanted_bricks": BrickInOfferQuantity.objects.filter(
                    offer=offer, side=Side.WANTED
                ),
                "button_action": get_button_action_for(logged_user, offer),
            }
        )

    context = base_context(request)
    context.update(
        {
            "offers_made": offers_made_context,
            "offers_received": offers_received_context,
        }
    )

    return render(
        request=request,
        template_name="bsf/exchange_offers.html",
        context=context,
    )


def exchange_items(request, offer):
    receivers_collection = UserCollection.objects.get(user=offer.offer_receiver)
    receivers_wishlist = Wishlist.objects.get(user=offer.offer_receiver)
    authors_collection = UserCollection.objects.get(user=offer.offer_author)
    authors_wishlist = Wishlist.objects.get(user=offer.offer_author)

    for set_in_offer in SetInOfferQuantity.objects.filter(offer=offer):
        rel = 1 if set_in_offer.side == Side.OFFERED else -1
        receivers_collection.modify_set_quantity(
            set_in_offer.legoset, rel * set_in_offer.quantity
        )
        authors_collection.modify_set_quantity(
            set_in_offer.legoset, -rel * set_in_offer.quantity
        )

        receivers_wishlist.modify_sets_quantity(
            set_in_offer.legoset,
            -set_in_offer.quantity,
            Side.WANTED if rel == 1 else Side.OFFERED,
        )
        authors_wishlist.modify_sets_quantity(
            set_in_offer.legoset,
            -set_in_offer.quantity,
            Side.OFFERED if rel == 1 else Side.WANTED,
        )

    for brick_in_offer in BrickInOfferQuantity.objects.filter(offer=offer):
        rel = 1 if brick_in_offer.side == Side.OFFERED else -1
        receivers_collection.modify_brick_quantity(
            brick_in_offer.brick, rel * brick_in_offer.quantity
        )
        authors_collection.modify_brick_quantity(
            brick_in_offer.brick, -rel * brick_in_offer.quantity
        )

        receivers_wishlist.modify_bricks_quantity(
            brick_in_offer.brick,
            -brick_in_offer.quantity,
            Side.WANTED if rel == 1 else Side.OFFERED,
        )
        authors_wishlist.modify_bricks_quantity(
            brick_in_offer.brick,
            -brick_in_offer.quantity,
            Side.OFFERED if rel == 1 else Side.WANTED,
        )

    offer.exchanged = True

    messages.info(request, "Items exchanged!")


def exchange_offer_continue(request):
    logged_user = request.user
    if not logged_user.is_authenticated:
        messages.error(request, "You need to be logged in to access brick exchange.")
        return redirect("exchange_offers")

    offer_id = request.POST.get("offer_accepted")
    if offer_id is None:
        messages.error(request, "Offer not found.")
        return redirect("exchange_offers")

    offer = ExchangeOffer.objects.get(pk=int(offer_id))
    is_author = offer.offer_author == logged_user

    match offer.author_state, offer.receiver_state:
        case _, ExchangeOffer.Status.PENDING:
            if not is_author:
                offer.receiver_state = ExchangeOffer.Status.ACCEPTED
                messages.success(request, "Offer accepted!")
        case _, ExchangeOffer.Status.ACCEPTED:
            if is_author:
                offer.author_state = ExchangeOffer.Status.EXCHANGED
            else:
                offer.receiver_state = ExchangeOffer.Status.EXCHANGED
            messages.success(request, "Items marked as exchanged successfully!")
        case ExchangeOffer.Status.ACCEPTED, ExchangeOffer.Status.EXCHANGED:
            if is_author:
                offer.author_state = ExchangeOffer.Status.EXCHANGED

    if (offer.author_state, offer.receiver_state) == (
            ExchangeOffer.Status.EXCHANGED,
            ExchangeOffer.Status.EXCHANGED,
    ):
        exchange_items(request, offer)
        messages.success(
            request, "Exchange completed and updated in system successfully!"
        )

    offer.save()

    return redirect("exchange_offers")


def exchange_offer_accepted(request):
    logged_user = request.user
    if not logged_user.is_authenticated:
        messages.error(request, "You need to be logged in to access brick exchange.")
        return redirect("index")

    offer_id = request.POST.get("offer_accepted")
    if offer_id is None:
        messages.error(request, "Offer not found.")
        return redirect("index")

    offer = ExchangeOffer.objects.get(pk=int(offer_id))

    exchange_items(offer)

    return redirect("index")


def exchange_delete_offer(request):
    logged_user = request.user
    if not logged_user.is_authenticated:
        messages.error(request, "You need to be logged in to access brick exchange.")
        return redirect("index")

    offer_id = request.POST.get("offer_id")
    if offer_id is None:
        messages.error(request, "Offer not found.")
        return redirect("index")

    offer = ExchangeOffer.objects.get(pk=int(offer_id))
    bioq_set = BrickInOfferQuantity.objects.filter(offer=offer)
    sioq_set = SetInOfferQuantity.objects.filter(offer=offer)

    for bioq in bioq_set:
        bioq.delete()

    for sioq in sioq_set:
        sioq.delete()

    offer.delete()

    return redirect("exchange_offers")


def generate_possible_offers(logged_user, other=None):
    """
    We are looking for users with whom we could trade bricks. They are sorted
    by min(what we can offer, what we can receive)
    """

    wanted_bricks = logged_user.wishlist_bricks.filter(side=Side.WANTED)
    offered_bricks = logged_user.wishlist_bricks.filter(side=Side.OFFERED)
    wanted_sets = logged_user.wishlist_sets.filter(side=Side.WANTED)
    offered_sets = logged_user.wishlist_sets.filter(side=Side.OFFERED)

    possible_offers = []
    if other is not None:
        possible_offers = [
            {
                "user": User.objects.get(username=other),
                "brick_quantity_offered": [],
                "brick_quantity_wanted": [],
                "set_quantity_offered": [],
                "set_quantity_wanted": [],
                "sum_offered": 0,
                "sum_wanted": 0,
            }
        ]
    else:
        for u in User.objects.all():
            if u != logged_user:
                possible_offers.append(
                    {
                        "user": u,
                        "brick_quantity_offered": [],
                        "brick_quantity_wanted": [],
                        "set_quantity_offered": [],
                        "set_quantity_wanted": [],
                        "sum_offered": 0,
                        "sum_wanted": 0,
                    }
                )

    for p_o in possible_offers:
        other_wanted_bricks = p_o["user"].wishlist_bricks.filter(side=Side.WANTED)
        other_offered_bricks = p_o["user"].wishlist_bricks.filter(side=Side.OFFERED)
        other_wanted_sets = p_o["user"].wishlist_sets.filter(side=Side.WANTED)
        other_offered_sets = p_o["user"].wishlist_sets.filter(side=Side.OFFERED)

        for brick_wanted in other_wanted_bricks:
            """Can we offer 'brick_wanted'"""
            if offered_bricks.filter(brick=brick_wanted.brick).exists():
                bricks_to_trade = min(
                    offered_bricks.filter(brick=brick_wanted.brick).get().quantity,
                    brick_wanted.quantity,
                )
                p_o["brick_quantity_offered"].append(
                    {"brick": brick_wanted.brick, "quantity": bricks_to_trade}
                )
                p_o["sum_offered"] += bricks_to_trade

        for brick_offered in other_offered_bricks:
            """Do we want 'brick_offered'"""
            if wanted_bricks.filter(brick=brick_offered.brick).exists():
                bricks_to_trade = min(
                    wanted_bricks.filter(brick=brick_offered.brick).get().quantity,
                    brick_offered.quantity,
                )
                p_o["brick_quantity_wanted"].append(
                    {"brick": brick_offered.brick, "quantity": bricks_to_trade}
                )
                p_o["sum_wanted"] += bricks_to_trade

        for set_wanted in other_wanted_sets:
            """Can we offer 'set_wanted'"""
            if offered_sets.filter(legoset=set_wanted.legoset).exists():
                sets_to_trade = min(
                    offered_sets.filter(legoset=set_wanted.legoset).get().quantity,
                    set_wanted.quantity,
                )
                p_o["set_quantity_offered"].append(
                    {"legoset": set_wanted.legoset, "quantity": sets_to_trade}
                )
                p_o["sum_offered"] += (
                        sets_to_trade * set_wanted.legoset.number_of_bricks()
                )

        for set_offered in other_offered_sets:
            """Do we want 'set_offered'"""
            if wanted_sets.filter(legoset=set_offered.legoset).exists():
                sets_to_trade = min(
                    wanted_sets.filter(legoset=set_offered.legoset).get().quantity,
                    set_offered.quantity,
                )
                p_o["set_quantity_wanted"].append(
                    {"legoset": set_offered.legoset, "quantity": sets_to_trade}
                )
                p_o["sum_wanted"] += (
                        sets_to_trade * set_offered.legoset.number_of_bricks()
                )

    possible_offers = [
        u for u in possible_offers if u["sum_offered"] + u["sum_wanted"] > 0
    ]
    sorted(
        possible_offers,
        key=lambda p_o: p_o["sum_offered"] + p_o["sum_wanted"],
        reverse=True,
    )
    return possible_offers
