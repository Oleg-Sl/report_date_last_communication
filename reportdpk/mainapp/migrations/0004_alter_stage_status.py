# Generated by Django 4.0.5 on 2022-06-12 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0003_alter_stage_direction'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stage',
            name='status',
            field=models.CharField(blank=True, choices=[('PREPARATION', 'Подготовка к работе'), ('WORK', 'В работе'), ('SUCCESSFUL', 'Успешна'), ('FAILURE', 'Провалена')], db_index=True, max_length=11, null=True),
        ),
    ]
