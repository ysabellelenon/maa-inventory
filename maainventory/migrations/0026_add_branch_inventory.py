# Generated manually - BranchInventory table for branch-level stock (Branches page)

import django.core.validators
from django.db import migrations, models
from django.db.models import deletion, Sum


def backfill_branch_inventory(apps, schema_editor):
    """Populate branches_inventory from current delivered requests minus consumption."""
    BranchInventory = apps.get_model('maainventory', 'BranchInventory')
    RequestItem = apps.get_model('maainventory', 'RequestItem')
    ItemConsumptionDaily = apps.get_model('maainventory', 'ItemConsumptionDaily')
    Branch = apps.get_model('maainventory', 'Branch')

    # Delivered per (branch_id, item_id, variation_id)
    delivered = {}
    for row in RequestItem.objects.filter(
        request__branch__is_active=True,
        request__status__in=['Delivered', 'Completed'],
        qty_fulfilled__gt=0
    ).values('request__branch_id', 'item_id', 'variation_id').annotate(
        total=Sum('qty_fulfilled')
    ):
        key = (row['request__branch_id'], row['item_id'], row['variation_id'])
        delivered[key] = row['total']

    # Consumed per (branch_id, item_id, variation_id)
    consumed = {}
    for row in ItemConsumptionDaily.objects.filter(
        branch__is_active=True
    ).values('branch_id', 'item_id', 'variation_id').annotate(
        total=Sum('qty_consumed')
    ):
        key = (row['branch_id'], row['item_id'], row['variation_id'])
        consumed[key] = row['total']

    to_create = []
    for (branch_id, item_id, variation_id), qty_delivered in delivered.items():
        qty_consumed = consumed.get((branch_id, item_id, variation_id), 0) or 0
        qty_available = max(0, float(qty_delivered) - float(qty_consumed))
        if qty_available <= 0:
            continue
        branch = Branch.objects.get(pk=branch_id)
        to_create.append(BranchInventory(
            branch_id=branch_id,
            brand_id=branch.brand_id,
            item_id=item_id,
            variation_id=variation_id,
            quantity=qty_available,
        ))
    if to_create:
        BranchInventory.objects.bulk_create(to_create)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('maainventory', '0025_remove_under_review_from_branch_requests'),
    ]

    operations = [
        migrations.CreateModel(
            name='BranchInventory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('branch', models.ForeignKey(on_delete=deletion.CASCADE, related_name='branch_inventory', to='maainventory.branch')),
                ('brand', models.ForeignKey(on_delete=deletion.CASCADE, related_name='branch_inventory', to='maainventory.brand')),
                ('item', models.ForeignKey(on_delete=deletion.CASCADE, related_name='branch_inventory', to='maainventory.item')),
                ('variation', models.ForeignKey(blank=True, null=True, on_delete=deletion.CASCADE, related_name='branch_inventory', to='maainventory.itemvariation')),
            ],
            options={
                'db_table': 'branches_inventory',
                'ordering': ['branch', 'item', 'variation'],
                'unique_together': {('branch', 'item', 'variation')},
            },
        ),
        migrations.RunPython(backfill_branch_inventory, noop),
    ]
