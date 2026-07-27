from celery import shared_task

from web.apps.payments.models import Payment


@shared_task
def update_payment_invoice_message_id_task(
        payment_id: int,
        invoice_message_id: int,
):
    Payment.objects.filter(id=payment_id).update(
        invoice_message_id=invoice_message_id,
    )
