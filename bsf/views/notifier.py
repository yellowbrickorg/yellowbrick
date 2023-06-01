from django.core.mail import send_mail, BadHeaderError
from django.template.loader import render_to_string
from ..constants import SENDER_EMAIL, DOMAIN_ADDR


def notify_about_new_offer(author, receiver, sets_in_offer, bricks_in_offer, cash,
                           is_a_counter):
    """
    Sends an email notifying the other person about the new offer

    Args:
        author : offer author
        receiver : offer receiver
        sets_in_offer : list of related SetsInOffer
        bricks_in_offer : list of related BricksInOffer
        cash : amount of cash to be offered/requested. cash > 0
            denotes author' offer, cash < 0 denotes author's request
        is_a_counter : indicates whether an offer is a counteroffer
    """
    subject = f"Counter offer from {author}" \
        if is_a_counter else f"New offer from {author}"

    context = {
        "email": receiver.email,
        "domain": DOMAIN_ADDR,
        "user": receiver,
        "sets_in_offer": sets_in_offer,
        "bricks_in_offer": bricks_in_offer,
        "cash": cash,
        "author": author,
        "protocol": "http",
    }
    if is_a_counter:
        message = render_to_string("bsf/exchange/offer_countered_notification.txt",
                                   context)
        html_message = render_to_string(
            "bsf/exchange/offer_countered_notification.html", context)
    else:
        message = render_to_string("bsf/exchange/new_offer_notification.txt", context)
        html_message = render_to_string("bsf/exchange/new_offer_notification.html",
                                        context)

    try:
        send_mail(
            subject=subject,
            from_email=SENDER_EMAIL,
            message=message,
            html_message=html_message,
            recipient_list=[receiver.email],
            fail_silently=False,
        )
    except BadHeaderError:
        pass


def _notify_about_offer_response(offer, is_accepted):
    """
    Sends a mail to offer owner that his offer got accepted/refused by a receiver.
    """
    response = "accepted" if is_accepted else "refused"
    subject = f"{offer.offer_receiver} {response} your offer"
    context = {
        "email": offer.offer_author.email,
        "message": DOMAIN_ADDR,
        "domain": DOMAIN_ADDR,
        "author": offer.offer_author,
        "receiver": offer.offer_receiver,
        "sets_in_offer": offer.setinofferquantity_set.all(),
        "bricks_in_offer": offer.brickinofferquantity_set.all(),
        "offered_cash": offer.offered_cash(),
        "wanted_cash": offer.wanted_cash(),
        "protocol": "http",
    }
    message = render_to_string(
        f"bsf/exchange/offer_{response}_notification.txt", context
    )
    html_message = render_to_string(
        f"bsf/exchange/offer_{response}_notification.html", context
    )
    try:
        send_mail(
            subject=subject,
            from_email=SENDER_EMAIL,
            message=message,
            html_message=html_message,
            recipient_list=[offer.offer_author.email],
            fail_silently=False,
        )
    except BadHeaderError:
        pass

def notify_about_offer_accepted(offer):
    _notify_about_offer_response(offer, True)


def notify_about_offer_refused(offer):
    _notify_about_offer_response(offer, False)


def notify_about_offer_exchanged(offer, is_to_author):
    """
    Sends a mail to offer owner that his offer got accepted/refused by a receiver.
    """
    exchanger = offer.offer_author
    email_receiver = offer.offer_receiver
    if is_to_author:
        exchanger, email_receiver = email_receiver, exchanger

    subject = f"{offer.offer_receiver} made an exchange in offer"
    context = {
        "email": email_receiver.email,
        "message": DOMAIN_ADDR,
        "domain": DOMAIN_ADDR,
        "exchanger": exchanger,
        "email_receiver": email_receiver,
        "protocol": "http",
    }
    message = render_to_string(
        f"bsf/exchange/offer_exchanged_notification.txt", context
    )
    html_message = render_to_string(
        f"bsf/exchange/offer_exchanged_notification.html", context
    )
    try:
        send_mail(
            subject=subject,
            from_email=SENDER_EMAIL,
            message=message,
            html_message=html_message,
            recipient_list=[email_receiver.email],
            fail_silently=False,
        )
    except BadHeaderError:
        pass
