from django.db import transaction

from bsf.models import (
    ExchangeOffer,
    BrickInOfferQuantity,
    SetInOfferQuantity,
    BrickInCollectionQuantity,
    SetInCollectionQuantity,
    Side,
    Wishlist,
    ExchangeChain,
)
from .base import *
from .notifier import (
    notify_about_new_offer,
    notify_about_offer_accepted,
    notify_about_offer_refused,
    notify_about_offer_exchanged,
)


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
                        messages.error(
                            request, "Can't offer more bricks than you have."
                        )
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


def form_offered_bricks_and_sets_lists(request, exchange_offer, possible_offers):
    bricks_in_offer = []
    sets_in_offer = []

    for side in [Side.OFFERED, Side.WANTED]:
        side_disp = "offer" if side == Side.OFFERED else "want"
        for brick in possible_offers[0][f"brick_quantity_{side_disp}ed"]:
            amount = request.POST.get(
                f"{side_disp}_brick_" + str(brick["brick"].brick_id)
            )
            if amount == "":
                continue
            amount = int(amount)
            if amount > 0:
                bioq = BrickInOfferQuantity(
                    offer=exchange_offer,
                    brick=brick["brick"],
                    quantity=amount,
                    side=side,
                )
                bricks_in_offer.append(bioq)

        for legoset in possible_offers[0][f"set_quantity_{side_disp}ed"]:
            amount = request.POST.get(f"{side_disp}_set_" + str(legoset["legoset"].id))
            if amount == "":
                continue
            amount = int(amount)
            if amount > 0:
                sioq = SetInOfferQuantity(
                    offer=exchange_offer,
                    legoset=legoset["legoset"],
                    quantity=amount,
                    side=side,
                )
                sets_in_offer.append(sioq)

    return bricks_in_offer, sets_in_offer


@transaction.atomic
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

    exchange_chain = ExchangeChain(initial_author=request.user, initial_receiver=other_user)

    exchange_offer = ExchangeOffer(
        offer_author=request.user,
        offer_receiver=other_user,
        exchange_chain=exchange_chain,
        which_in_order=1
    )

    bricks_in_offer, sets_in_offer = form_offered_bricks_and_sets_lists(
        request, exchange_offer, possible_offers
    )

    if len(bricks_in_offer) + len(sets_in_offer) == 0:
        messages.error(request, "Can't submit an empty offer.")
        return redirect("exchange")

    exchange_chain.save()
    exchange_offer.save()
    for bioq in bricks_in_offer:
        bioq.save()

    for sioq in sets_in_offer:
        sioq.save()

    notify_about_new_offer(logged_user, other_user, sets_in_offer, bricks_in_offer)

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

    offers_made, offers_received = get_related_offers(logged_user)

    offers_made_context = create_offers_context(logged_user, offers_made)
    offers_received_context = create_offers_context(logged_user, offers_received)

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


def create_offers_context(logged_user, offers):
    context = []
    for offer in offers:
        context.append(
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
    return context


@transaction.atomic
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
                notify_about_offer_accepted(offer)
        case _, ExchangeOffer.Status.ACCEPTED:
            if is_author:
                offer.author_state = ExchangeOffer.Status.EXCHANGED
            else:
                offer.receiver_state = ExchangeOffer.Status.EXCHANGED
            messages.success(request, "Items marked as exchanged successfully!")
            notify_about_offer_exchanged(offer, not is_author)
        case ExchangeOffer.Status.ACCEPTED, ExchangeOffer.Status.EXCHANGED:
            if is_author:
                offer.author_state = ExchangeOffer.Status.EXCHANGED
                notify_about_offer_exchanged(offer, not is_author)

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
    offer.receiver_state = ExchangeOffer.Status.REFUSED
    offer.save()

    if logged_user == offer.offer_receiver:
        notify_about_offer_refused(offer)

    return redirect("exchange_offers")


def dict_offer_base(user):
    return {
        "user": user,
        "brick_quantity_offered": [],
        "brick_quantity_wanted": [],
        "set_quantity_offered": [],
        "set_quantity_wanted": [],
        "sum_offered": 0,
        "sum_wanted": 0,
    }


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
        possible_offers = [dict_offer_base(User.objects.get(username=other))]
    else:
        for user in User.objects.all():
            if user != logged_user:
                possible_offers.append(dict_offer_base(user))

    for offers in possible_offers:
        other_bricks_wishlist = offers["user"].wishlist_bricks.all()
        other_sets_wishlist = offers["user"].wishlist_sets.all()

        for brick_wish in other_bricks_wishlist:
            side_disp = "offer" if brick_wish.side == Side.OFFERED else "want"
            opposite_list = (
                wanted_bricks if brick_wish.side == Side.OFFERED else offered_bricks
            )
            qty = opposite_list.filter(brick=brick_wish.brick).count()
            if qty > 0:
                bricks_to_trade = min(qty, brick_wish.quantity)
                offers[f"brick_quantity_{side_disp}ed"].append(
                    {"brick": brick_wish.brick, "quantity": bricks_to_trade}
                )
                offers[f"sum_{side_disp}ed"] += bricks_to_trade

        for set_wish in other_sets_wishlist:
            side_disp = "offer" if set_wish.side == Side.OFFERED else "want"
            opposite_list = (
                wanted_sets if set_wish.side == Side.OFFERED else offered_sets
            )
            qty = opposite_list.filter(legoset=set_wish.legoset).count()
            if qty > 0:
                sets_to_trade = min(qty, set_wish.quantity)
                offers[f"set_quantity_{side_disp}ed"].append(
                    {"legoset": set_wish.legoset, "quantity": sets_to_trade}
                )
                offers[f"sum_{side_disp}ed"] += (
                        sets_to_trade * set_wish.legoset.number_of_bricks()
                )

    possible_offers = [
        offers
        for offers in possible_offers
        if offers["sum_offered"] + offers["sum_wanted"] > 0
    ]
    sorted(
        possible_offers,
        key=lambda offers: offers["sum_offered"] + offers["sum_wanted"],
        reverse=True,
    )
    return possible_offers


def get_related_offers(user):
    offers_made = []
    offers_received = []

    chains = []
    for chain in ExchangeChain.objects.filter(initial_author = user):
        chains.append(chain)

    for chain in ExchangeChain.objects.filter(initial_receiver = user):
        chains.append(chain)

    for chain in chains:
        offer = chain.get_last_offer()
        """ We don't show refused offers as if they were deleted """
        if offer.receiver_state != ExchangeOffer.Status.REFUSED:
            if offer.offer_author == user:
                offers_made.append(offer)
            else:
                offers_received.append(offer)
    return offers_made, offers_received


def offer_details(request):
    logged_user = request.user
    if not logged_user.is_authenticated:
        messages.error(request, "You need to be logged in to access brick exchange.")
        return redirect("index")
    
    offer_id = request.POST.get("offer_id")
    if offer_id is None:
        messages.error(request, "Offer not found.")
        return redirect("index")
    offer_clicked = ExchangeOffer.objects.get(id=offer_id)
    counteroffer_jump = ( request.POST.get("counteroffer") is not None )
    chain = offer_clicked.exchange_chain
    all_offers = chain.related_offers.all()
    sorted(all_offers, key=lambda offer : offer.which_in_order)

    all_offers_context = []
    authored = ( chain.initial_author == logged_user )
    for offer in all_offers:
        if authored:
            all_offers_context.append(
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
                }
            )
        else:
            all_offers_context.append(
                {
                    "offer": offer,
                    "offered_sets": SetInOfferQuantity.objects.filter(
                        offer=offer, side=Side.WANTED
                    ),
                    "offered_bricks": BrickInOfferQuantity.objects.filter(
                        offer=offer, side=Side.WANTED
                    ),
                    "wanted_sets": SetInOfferQuantity.objects.filter(
                        offer=offer, side=Side.OFFERED
                    ),
                    "wanted_bricks": BrickInOfferQuantity.objects.filter(
                        offer=offer, side=Side.OFFERED
                    ),
                }
            )
        authored = not authored
    
    """
    sprawdzanie czy mozna robic kontroferte i dodawanie do kontekstu
    nie wiem 
    """
    last_offer = all_offers[len(all_offers) - 1]
    may_counteroffer = False
    if last_offer.offer_author != logged_user and last_offer.receiver_state == ExchangeOffer.Status.PENDING:
        may_counteroffer = True
    
    other_user = None
    if offer_clicked.offer_author == logged_user:
        other_user = offer_clicked.offer_receiver
    else:
        other_user = offer_clicked.offer_author
    possible_offer = generate_possible_offers(logged_user, other_user)

    context = {
        "other_user" : other_user,
        "offers_history" : all_offers_context,
        "may_counteroffer" : may_counteroffer,
        "possible_offer" : possible_offer[0],
        "jump_to_counteroffer" : counteroffer_jump,
        "chain_id" : chain.id,
    }

    return render(
        request=request,
        context=context,
        template_name="bsf/exchange/offer_details.html",
    )


def counteroffer_continue(request):
    logged_user = request.user
    if not logged_user.is_authenticated:
        messages.error(request, "You need to be logged in to access brick exchange.")
        return redirect("index")
    
    chain_id = request.POST.get("chain_id")
    if chain_id is None:
        messages.error(request, "Offer not found.")
        return redirect("index")
    chain = ExchangeChain.objects.get(id = chain_id)

    other_user = None
    if chain.initial_author == logged_user:
        other_user = chain.initial_receiver
    else:
        other_user = chain.initial_author

    possible_offers = generate_possible_offers(logged_user, other_user)

    exchange_offer = ExchangeOffer(
        offer_author=logged_user,
        offer_receiver=other_user,
        exchange_chain=chain,
        which_in_order=chain.get_next_number(),
    )

    bricks_in_offer, sets_in_offer = form_offered_bricks_and_sets_lists(
        request, exchange_offer, possible_offers
    )

    if len(bricks_in_offer) + len(sets_in_offer) == 0:
        messages.error(request, "Can't submit an empty offer.")
        return redirect("exchange_offers")

    chain.save()
    exchange_offer.save()
    for bioq in bricks_in_offer:
        bioq.save()

    for sioq in sets_in_offer:
        sioq.save()
    
    notify_about_new_offer(logged_user, other_user, sets_in_offer, bricks_in_offer)

    return redirect("exchange_offers")