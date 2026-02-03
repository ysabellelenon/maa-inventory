# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('maainventory', '0023_branch_packaging_items'),
    ]

    operations = [
        # Make packaging_item nullable (was required, now optional for backward compatibility)
        migrations.AlterField(
            model_name='branchpackagingruleitem',
            name='packaging_item',
            field=models.ForeignKey(
                blank=True,
                help_text='Legacy: generic packaging type',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='rule_items',
                to='maainventory.branchpackagingitem'
            ),
        ),
        # Add inventory_item FK to link to warehouse inventory
        migrations.AddField(
            model_name='branchpackagingruleitem',
            name='inventory_item',
            field=models.ForeignKey(
                blank=True,
                help_text='Warehouse inventory item used as packaging',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='packaging_rule_items',
                to='maainventory.item'
            ),
        ),
        # Remove unique_together constraint on ('rule', 'packaging_item') since packaging_item is now optional
        migrations.AlterUniqueTogether(
            name='branchpackagingruleitem',
            unique_together=set(),
        ),
    ]
