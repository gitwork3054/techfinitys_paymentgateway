from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [('portal', '0001_initial')]
    operations = [
        migrations.AlterField(model_name='payment', name='status', field=models.CharField(choices=[('pending','Pending'),('paid','Paid'),('failed','Failed')], default='pending', max_length=10)),
        migrations.AddField(model_name='payment', name='provider', field=models.CharField(blank=True, max_length=30)),
        migrations.AddField(model_name='payment', name='provider_order_id', field=models.CharField(blank=True, db_index=True, max_length=80)),
        migrations.AddField(model_name='payment', name='provider_payment_id', field=models.CharField(blank=True, db_index=True, max_length=100)),
    ]
