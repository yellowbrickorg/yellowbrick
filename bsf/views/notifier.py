from django.core.mail import send_mail, BadHeaderError
from django.template.loader import render_to_string
from ..constants import SENDER_EMAIL, DOMAIN_ADDR


def notify_about_new_offer(author, receiver, sets_in_offer, bricks_in_offer):
    """
    Sends an email notifying the other person about the new offer

    Args:
        author : offer author
        receiver : offer receiver
        sets_in_offer : list of related SetsInOffer
        bricks_in_offer : list of related BricksInOffer
    """
    subject = f"New offer from {author}"
    context = {
        "email": receiver.email,
        "domain": DOMAIN_ADDR,
        "user": receiver,
        "sets_in_offer": sets_in_offer,
        "bricks_in_offer": bricks_in_offer,
        "author": author,
        "protocol": "http",
    }
    message = render_to_string("bsf/exchange/new_offer_notification.txt", context)
    html_message = render_to_string("bsf/exchange/new_offer_notification.html", context)
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
