# Generated manually - remove Under Review status from branch requests

from django.db import migrations


def set_under_review_to_pending(apps, schema_editor):
    Request = apps.get_model('maainventory', 'Request')
    Request.objects.filter(status='UnderReview').update(status='Pending')


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('maainventory', '0024_add_inventory_item_to_packaging_rule'),
    ]

    operations = [
        migrations.RunPython(set_under_review_to_pending, noop),
    ]
